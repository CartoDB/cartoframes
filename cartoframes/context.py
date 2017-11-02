"""CartoContext and BatchJobStatus classes"""
import json
import os
import random
import sys
import time
import collections
import binascii as ba
from warnings import warn

import requests
import IPython
import pandas as pd
from tqdm import tqdm
from appdirs import user_cache_dir

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient, BatchSQLClient
from carto.exceptions import CartoException

from .credentials import Credentials
from .utils import (dict_items, normalize_colnames, norm_colname,
                    importify_params, join_url)
from .layer import BaseMap
from .maps import non_basemap_layers, get_map_name, get_map_template
from .__version__ import __version__

if sys.version_info >= (3, 0):
    from urllib.parse import urlparse, urlencode
else:
    from urlparse import urlparse
    from urllib import urlencode
try:
    import matplotlib.image as mpi
    import matplotlib.pyplot as plt
    # set dpi based on CARTO Static Maps API dpi
    mpi.rcParams['figure.dpi'] = 72.0
except (ImportError, RuntimeError):
    mpi = None
    plt = None
HAS_MATPLOTLIB = plt is not None

# Choose constant to avoid overview generation which are triggered at a
# half million rows
MAX_IMPORT_ROWS = 499999

# threshold for using batch sql api or not for geometry creation
MAX_ROWS_LNGLAT = 100000

# Cache directory for temporary data operations
CACHE_DIR = user_cache_dir('cartoframes')

# cartoframes version
DEFAULT_SQL_ARGS = dict(client='cartoframes_{}'.format(__version__),
                        do_post=False)


class CartoContext(object):
    """CartoContext class for authentication with CARTO and high-level operations
    such as reading tables from CARTO into dataframes, writing dataframes to
    CARTO tables, creating custom maps from dataframes and CARTO tables, and
    augmenting data using CARTO's `Data Observatory
    <https://carto.com/data-observatory>`__. Future methods will interact with
    CARTO's services like `routing, geocoding, and isolines
    <https://carto.com/location-data-services/>`__, PostGIS backend for spatial
    processing, and much more.

    Manages connections with CARTO for data and map operations. Modeled
    after `SparkContext
    <https://jaceklaskowski.gitbooks.io/mastering-apache-spark/content/spark-sparkcontext.html>`__.

    Attributes:
        creds (cartoframes.Credentials): :obj:`Credentials` instance

    Args:
        base_url (str): Base URL of CARTO user account. Cloud-based accounts
            are of the form ``https://{username}.carto.com`` (e.g.,
            https://eschbacher.carto.com for user ``eschbacher``). On-premises
            installation users should ask their admin.
        api_key (str): CARTO API key.
        session (requests.Session, optional): requests session. See `requests
            documentation
            <http://docs.python-requests.org/en/master/user/advanced/>`__
            for more information.
        verbose (bool, optional): Output underlying process states (True), or
            suppress (False, default)

    Returns:
        :obj:`CartoContext`: A CartoContext object that is authenticated
        against the user's CARTO account.

    Example:
        Create a CartoContext object::

            import cartoframes
            cc = cartoframes.CartoContext(BASEURL, APIKEY)
    """
    def __init__(self, base_url=None, api_key=None, creds=None, session=None,
                 verbose=0):

        self.creds = Credentials(creds=creds, key=api_key, base_url=base_url)
        self.auth_client = APIKeyAuthClient(base_url=self.creds.base_url(),
                                            api_key=self.creds.key(),
                                            session=session)
        self.sql_client = SQLClient(self.auth_client)
        self.creds.username(self.auth_client.username)
        self.is_org = self._is_org_user()

        self._map_templates = {}
        self._srcdoc = None
        self._verbose = verbose

    def _is_org_user(self):
        """Report whether user is in a multiuser CARTO organization or not"""
        res = self.sql_client.send('SHOW search_path', **DEFAULT_SQL_ARGS)

        paths = [p.strip() for p in res['rows'][0]['search_path'].split(',')]
        # is an org user if first item is not `public`
        return paths[0] != 'public'

    def read(self, table_name, limit=None, index='cartodb_id',
             decode_geom=False):
        """Read a table from CARTO into a pandas DataFrames.

        Args:
            table_name (str): Name of table in user's CARTO account.
            limit (int, optional): Read only `limit` lines from
                `table_name`. Defaults to ``None``, which reads the full table.
            index (str, optional): Not currently in use.
            decode_geom (bool, optional): Decodes CARTO's geometries into a
              `Shapely <https://github.com/Toblerity/Shapely>`__
              object that can be used, for example, in `GeoPandas
              <http://geopandas.org/>`__.

        Returns:
            pandas.DataFrame: DataFrame representation of `table_name` from
            CARTO.

        Example:
            .. code:: python

                import cartoframes
                cc = cartoframes.CartoContext(BASEURL, APIKEY)
                df = cc.read('acadia_biodiversity')
        """
        query = 'SELECT * FROM "{table_name}"'.format(table_name=table_name)
        if limit is not None:
            if isinstance(limit, int) and (limit >= 0):
                query += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")

        return self.query(query, decode_geom=decode_geom)

    def write(self, df, table_name, temp_dir=CACHE_DIR,
              overwrite=False, lnglat=None, encode_geom=False, geom_col=None,
              **kwargs):
        """Write a DataFrame to a CARTO table.

        Example:
            Write a pandas DataFrame to CARTO.

            .. code:: python

                cc.write(df, 'brooklyn_poverty', overwrite=True)

            Scrape an HTML table from Wikipedia and send to CARTO with content
            guessing to create a geometry from the country column. This uses
            a CARTO Import API param `content_guessing` parameter.

            .. code:: python

                url = 'https://en.wikipedia.org/wiki/List_of_countries_by_life_expectancy'
                # retrieve first HTML table from that page
                df = pd.read_html(url, header=0)[0]
                # send to carto, let it guess polygons based on the 'country'
                #   column. Also set privacy to 'public'
                cc.write(df, 'life_expectancy',
                         content_guessing=True,
                         privacy='public')
                cc.map(layers=Layer('life_expectancy',
                                    color='both_sexes_life_expectancy'))

        Args:
            df (pandas.DataFrame): DataFrame to write to ``table_name`` in user
                CARTO account
            table_name (str): Table to write ``df`` to in CARTO.
            temp_dir (str, optional): Directory for temporary storage of data
                that is sent to CARTO. Default is ``/tmp`` (Unix-like systems).
            overwrite (bool, optional): Behavior for overwriting ``table_name``
                if it exits on CARTO. Defaults to ``False``.
            lnglat (tuple, optional): lng/lat pair that can be used for
                creating a geometry on CARTO. Defaults to ``None``. In some
                cases, geometry will be created without specifying this. See
                CARTO's `Import API
                <https://carto.com/docs/carto-engine/import-api/standard-tables>`__
                for more information.
            encode_geom (bool, optional): Whether to write `geom_col` to CARTO
                as `the_geom`.
            geom_col (str, optional): The name of the column where geometry
                information is stored. Used in conjunction with `encode_geom`.
            kwargs: Keyword arguments from CARTO's Import API. See the `params
                listed in the documentation
                <https://carto.com/docs/carto-engine/import-api/standard-tables/#params>`__
                for more information. For example, when using
                `content_guessing='true'`, a column named 'countries' with
                country names will be used to generate polygons for each
                country. To avoid unintended consequences, avoid `file`, `url`,
                and other similar arguments.

        Returns:
            :obj:`BatchJobStatus` or None: If `lnglat` flag is set and the
            DataFrame has more than 100,000 rows, a :obj:`BatchJobStatus`
            instance is returned. Otherwise, None.

        .. note::
            DataFrame indexes are changed to ordinary columns. CARTO creates
            an index called `cartodb_id` for every table that runs from 1 to
            the length of the DataFrame.
        """  # noqa
        # work on a copy to avoid changing the original
        _df = df.copy()
        if not os.path.exists(temp_dir):
            self._debug_print(temp_dir='creating directory at ' + temp_dir)
            os.makedirs(temp_dir)
        if encode_geom:
            _add_encoded_geom(_df, geom_col)

        if not overwrite:
            # error if table exists and user does not want to overwrite
            self._table_exists(table_name)

        # issue warning if the index is anything but the pandas default
        #  range index
        if not _df.index.equals(pd.RangeIndex(0, _df.shape[0], 1)):
            _df.reset_index(inplace=True)

        pgcolnames = normalize_colnames(_df.columns)
        if table_name != norm_colname(table_name):
            table_name = norm_colname(table_name)
            warn('Table will be named `{}`'.format(table_name))

        if _df.shape[0] > MAX_IMPORT_ROWS:
            # NOTE: schema is set using different method than in _set_schema
            # send placeholder table
            final_table_name = self._send_dataframe(_df.iloc[0:0], table_name,
                                                    temp_dir, geom_col,
                                                    pgcolnames, kwargs)
            # send dataframe in batches, combine into placeholder table
            final_table_name = self._send_batches(_df, table_name, temp_dir,
                                                  geom_col, pgcolnames, kwargs)
        else:
            final_table_name = self._send_dataframe(_df, table_name, temp_dir,
                                                    geom_col, pgcolnames,
                                                    kwargs)
            self._set_schema(_df, final_table_name, pgcolnames)

        # create geometry column from long/lats if requested
        if lnglat:
            query = '''
                    UPDATE "{table_name}"
                    SET the_geom = CDB_LatLng("{lat}"::numeric,
                                              "{lng}"::numeric);
                    SELECT CDB_TableMetadataTouch('{table_name}'::regclass);
                    '''.format(table_name=final_table_name,
                               lng=norm_colname(lnglat[0]),
                               lat=norm_colname(lnglat[1]))
            if _df.shape[0] > MAX_ROWS_LNGLAT:
                batch_client = BatchSQLClient(self.auth_client)
                status = batch_client.create([query, ])
                tqdm.write(
                    'Table successfully written to CARTO: {table_url}\n'
                    '`the_geom` column is being populated from `{lnglat}`. '
                    'Check the status of the operation with:\n'
                    '    \033[1mBatchJobStatus(CartoContext(), \'{job_id}\''
                    ').status()\033[0m\n'
                    'or try reading the table from CARTO in a couple of '
                    'minutes.\n'
                    '\033[1mNote:\033[0m `CartoContext.map` will not work on '
                    'this table until its geometries are created.'.format(
                               table_url=join_url((self.creds.base_url(),
                                                   'dataset',
                                                   final_table_name, )),
                               job_id=status.get('job_id'),
                               lnglat=str(lnglat)))
                return BatchJobStatus(self, status)

            self.sql_client.send(query, do_post=False)

        tqdm.write('Table successfully written to CARTO: {table_url}'.format(
                       table_url=join_url((self.creds.base_url(),
                                           'dataset',
                                           final_table_name, ))))

    def delete(self, table_name):
        """Delete a table in user's CARTO account.

        Args:
            table_name (str): Table name to delete

        Returns:
            None
        """
        try:
            resp = self.auth_client.send(
                'api/v1/viz/{table_name}'.format(table_name=table_name),
                http_method='DELETE'
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            warn('Failed to delete the following table from CARTO '
                 'account: `{table_name}`. ({err})'.format(
                     table_name=table_name,
                     err=err))
        return None

    def _table_exists(self, table_name):
        """Checks to see if table exists"""
        try:
            self.sql_client.send('''
                EXPLAIN SELECT * FROM "{table_name}"
                '''.format(table_name=table_name),
                do_post=False)
            raise NameError(
                'Table `{table_name}` already exists. '
                'Run with `overwrite=True` if you wish to replace the '
                'table.'.format(table_name=table_name))
        except CartoException as err:
            # If table doesn't exist, we get an error from the SQL API
            self._debug_print(err=err)
            return False

    def _send_batches(self, df, table_name, temp_dir, geom_col, pgcolnames,
                      kwargs):
        """Batch sending a dataframe in chunks that are then recombined.

        Args:
            df (pandas.DataFrame): DataFrame that will be batched up for
                sending to CARTO
            table_name (str): Name of table to send DataFrame to
            temp_dir (str): Local directory for temporary storage of DataFrame
                written to file that will be sent to CARTO
            geom_col (str): Name of encoded geometry column (if any) that will
                be dropped or converted to `the_geom` column
            pgcolnames (list of str): List of SQL-normalized column names

        Returns:
            final_table_name (str): Final table name on CARTO that the
            DataFrame is stored in
        """
        subtables = []
        # generator for accessing chunks of original dataframe
        df_gen = df.groupby(list(i // MAX_IMPORT_ROWS
                                 for i in range(df.shape[0])))
        for chunk_num, chunk in tqdm(df_gen.__iter__(),
                                     total=df.shape[0] // MAX_IMPORT_ROWS + 1,
                                     desc='Uploading in batches'):
            temp_table = '{orig}_cartoframes_temp_{chunk}'.format(
                orig=table_name[:40],
                chunk=chunk_num)
            try:
                # send dataframe chunk, get new name if collision
                temp_table = self._send_dataframe(chunk, temp_table, temp_dir,
                                                  geom_col, pgcolnames, kwargs)
            except CartoException as err:
                for table in subtables:
                    self.delete(table)
                self.delete(table_name)
                raise CartoException(err)

            if temp_table:
                subtables.append(temp_table)
            self._debug_print(chunk_num=chunk_num,
                              chunk_shape=str(chunk.shape),
                              temp_table=temp_table)

        # combine chunks into final table
        try:
            select_base = 'SELECT {schema} FROM "{{table}}"'.format(
                schema=_df2pg_schema(df, pgcolnames))
            unioned_tables = '\nUNION ALL\n'.join([select_base.format(table=t)
                                                   for t in subtables])
            self._debug_print(unioned=unioned_tables)
            drop_tables = '\n'.join(
                    'DROP TABLE IF EXISTS "{table}";'.format(table=table)
                    for table in subtables)
            # 1. create temp table for all the data
            # 2. drop all previous temp tables
            # 3. drop placeholder table and move temp table into it's place
            # 4. cartodb-fy table, register it with metadata
            query = '''
                CREATE TABLE "{table_name}_temp" As {unioned_tables};
                ALTER TABLE "{table_name}_temp"
                      DROP COLUMN IF EXISTS cartodb_id;
                {drop_tables}
                DROP TABLE IF EXISTS "{table_name}";
                ALTER TABLE "{table_name}_temp" RENAME TO "{table_name}";
                SELECT CDB_CartoDBFYTable('{org}', '{table_name}');
                SELECT CDB_TableMetadataTouch('{table_name}'::regclass);
                '''.format(table_name=table_name,
                           unioned_tables=unioned_tables,
                           org=(self.creds.username()
                                if self.is_org else 'public'),
                           drop_tables=drop_tables)
            self._debug_print(query=query)
            self.sql_client.send(query, **DEFAULT_SQL_ARGS)
        except CartoException as err:
            for table in subtables:
                self.delete(table)
            self.delete(table_name)
            raise Exception('Failed to upload dataframe: {}'.format(err))

        return table_name

    def _send_dataframe(self, df, table_name, temp_dir, geom_col, pgcolnames,
                        kwargs):
        """Send a DataFrame to CARTO to be imported as a SQL table. Index of
            DataFrame not included.

        Note:
            Schema from ``df`` is not enforced with this method. Use
            ``self._set_schema`` to enforce the schema.

        Args:
            df (pandas.DataFrame): DataFrame that is will be sent to CARTO
            table_name (str): Name on CARTO for the table that will have the
                data from ``df``
            temp_dir (str): Name of directory used for temporarily storing the
                DataFrame file to sent to CARTO
            geom_col (str): Name of geometry column

        Returns:
            final_table_name (str): Name of final table. This method will
            overwrite the table `table_name` if it already exists.
        """
        def remove_tempfile(filepath):
            """removes temporary file"""
            os.remove(filepath)

        tempfile = '{temp_dir}/{table_name}.csv'.format(temp_dir=temp_dir,
                                                        table_name=table_name)
        self._debug_print(tempfile=tempfile)
        df.drop(labels=[geom_col], axis=1, errors='ignore').to_csv(
                path_or_buf=tempfile,
                na_rep='',
                header=pgcolnames,
                index=False,
                encoding='utf-8')

        with open(tempfile, 'rb') as f:
            params = {'type_guessing': False}
            params.update(kwargs)
            params = {k: importify_params(v) for k, v in dict_items(params)}
            res = self._auth_send('api/v1/imports', 'POST',
                                  files={'file': f},
                                  params=params,
                                  stream=True)
            self._debug_print(res=res)

            if not res.get('success'):
                remove_tempfile(tempfile)
                raise CartoException('Failed to send DataFrame')
            import_id = res['item_queue_id']

        remove_tempfile(tempfile)
        final_table_name = table_name
        while True:
            import_job = self._check_import(import_id)
            self._debug_print(import_job=import_job)
            final_table_name = self._handle_import(import_job, table_name)
            if import_job['state'] == 'complete':
                break
            # Wait a second before doing another request
            time.sleep(1.0)

        return final_table_name

    def _set_schema(self, dataframe, table_name, pgcolnames):
        """Update a table associated with a dataframe to have the equivalent
        schema

        Args:
            dataframe (pandas.DataFrame): Dataframe that CARTO table is cloned
                from
            table_name (str): Table name where schema is being altered
            pgcolnames (list of str): List of column names from ``dataframe``
                as they appear on the database
        Returns:
            None
        """
        util_cols = ('the_geom', 'the_geom_webmercator', 'cartodb_id')
        alter_temp = ('ALTER COLUMN "{col}" TYPE {ctype} USING '
                      'NULLIF("{col}", \'\')::{ctype}')
        # alter non-util columns that are not text type
        alter_cols = ', '.join(alter_temp.format(col=c,
                                                 ctype=_dtypes2pg(t))
                               for c, t in zip(pgcolnames,
                                               dataframe.dtypes)
                               if c not in util_cols and t != 'object')
        alter_query = 'ALTER TABLE "{table}" {alter_cols};'.format(
            table=table_name,
            alter_cols=alter_cols)
        self._debug_print(alter_query=alter_query)
        try:
            self.sql_client.send(alter_query, **DEFAULT_SQL_ARGS)
        except CartoException as err:
            warn('DataFrame written to CARTO but the table schema failed to '
                 'update to match DataFrame. All columns in CARTO table have '
                 'data type `text`. CARTO error: `{err}`.'.format(
                     err=err,
                     query=alter_query))

    def _check_import(self, import_id):
        """Check the status of an Import API job"""

        res = self._auth_send('api/v1/imports/{}'.format(import_id),
                              'GET')
        return res

    def _handle_import(self, import_job, table_name):
        """Handle state of import job"""
        if import_job['state'] == 'failure':
            if import_job['error_code'] == 8001:
                raise CartoException('Over CARTO account storage limit for '
                                     'user `{}`. Try subsetting your '
                                     'DataFrame or dropping columns to reduce '
                                     'the data size.'.format(
                                         self.creds.username()))
            elif import_job['error_code'] == 6668:
                raise CartoException('Too many rows in DataFrame. Try '
                                     'subsetting DataFrame before writing to '
                                     'CARTO.')
            else:
                raise CartoException('Error code: `{}`. See CARTO Import '
                                     'API error documentation for more '
                                     'information: https://carto.com/docs/'
                                     'carto-engine/import-api/import-errors'
                                     ''.format(import_job['error_code']))
        elif import_job['state'] == 'complete':
            self._debug_print(final_table=import_job['table_name'])
            if import_job['table_name'] != table_name:
                try:
                    res = self.sql_client.send('''
                            DROP TABLE IF EXISTS {orig_table};
                            ALTER TABLE {dupe_table} RENAME TO {orig_table};
                            SELECT CDB_TableMetadataTouch(
                                       '{orig_table}'::regclass);
                            '''.format(
                                orig_table=table_name,
                                dupe_table=import_job['table_name']),
                            do_post=False)

                    self._debug_print(res=res)
                except Exception as err:
                    self._debug_print(err=err)
                    raise Exception('Cannot overwrite table `{table_name}` '
                                    '({err}). DataFrame was written to '
                                    '`{new_table}` instead.'.format(
                                        table_name=table_name,
                                        err=err,
                                        new_table=import_job['table_name']))
        return table_name

    def sync(self, dataframe, table_name):
        """Depending on the size of the DataFrame or CARTO table, perform
        granular operations on a DataFrame to only update the changed cells
        instead of a bulk upload. If on the large side, perform granular
        operations, if on the smaller side use Import API.

        Note:
            Not yet implemented.
        """
        pass

    def query(self, query, table_name=None, decode_geom=False):
        """Pull the result from an arbitrary SQL query from a CARTO account
        into a pandas DataFrame. Can also be used to perform database
        operations (creating/dropping tables, adding columns, updates, etc.).

        Args:
            query (str): Query to run against CARTO user database. This data
              will then be converted into a pandas DataFrame.
            table_name (str, optional): If set, this will create a new
              table in the user's CARTO account that is the result of the
              query. Defaults to None (no table created).
            decode_geom (bool, optional): Decodes CARTO's geometries into a
              `Shapely <https://github.com/Toblerity/Shapely>`__
              object that can be used, for example, in `GeoPandas
              <http://geopandas.org/>`__.

        Returns:
            pandas.DataFrame: DataFrame representation of query supplied.
            Pandas data types are inferred from PostgreSQL data types.
            In the case of PostgreSQL date types, dates are attempted to be
            converted, but on failure a data type 'object' is used.
        """
        self._debug_print(query=query)
        if table_name:
            create_table_query = '''
                CREATE TABLE {table_name} As
                SELECT *
                  FROM ({query}) As _wrap;
                SELECT CDB_CartodbfyTable('{org}', '{table_name}');
            '''.format(table_name=table_name,
                       query=query,
                       org=(self.creds.username()
                            if self.is_org else 'public'))
            self._debug_print(create_table_query=create_table_query)

            create_table_res = self.sql_client.send(create_table_query,
                                                    do_post=False)
            self._debug_print(create_table_res=create_table_res)

            new_table_name = create_table_res['rows'][0]['cdb_cartodbfytable']
            self._debug_print(new_table_name=new_table_name)

            select_res = self.sql_client.send(
                'SELECT * FROM {table_name}'.format(table_name=new_table_name),
                **DEFAULT_SQL_ARGS)
        else:
            skipfields = ('the_geom_webmercator'
                          if 'the_geom_webmercator' not in query else None)
            select_res = self.sql_client.send(query,
                                              skipfields=skipfields,
                                              **DEFAULT_SQL_ARGS)

        self._debug_print(select_res=select_res)

        fields = select_res['fields']
        if select_res['total_rows'] == 0:
            return pd.DataFrame(columns=set(fields.keys()) - {'cartodb_id'})

        df = pd.DataFrame(data=select_res['rows'])
        for field in fields:
            if fields[field]['type'] == 'date':
                df[field] = pd.to_datetime(df[field], errors='ignore')

        self._debug_print(columns=df.columns,
                          dtypes=df.dtypes)

        if 'cartodb_id' in fields:
            df.set_index('cartodb_id', inplace=True)

        if decode_geom:
            df['geometry'] = df.the_geom.apply(_decode_geom)

        return df

    def map(self, layers=None, interactive=True,
            zoom=None, lat=None, lng=None, size=(800, 400),
            ax=None):
        """Produce a CARTO map visualizing data layers.

        Examples:
            Create a map with two data layers, and one BaseMap layer::

                import cartoframes
                from cartoframes import Layer, BaseMap, styling
                cc = cartoframes.CartoContext(BASEURL, APIKEY)
                cc.map(layers=[BaseMap(),
                               Layer('acadia_biodiversity',
                                     color={'column': 'simpson_index',
                                            'scheme': styling.tealRose(7)}),
                               Layer('peregrine_falcon_nest_sites',
                                     size='num_eggs',
                                     color={'column': 'bird_id',
                                            'scheme': styling.vivid(10))],
                       interactive=True)

            Create a snapshot of a map at a specific zoom and center::

                cc.map(layers=Layer('acadia_biodiversity',
                                    color='simpson_index'),
                       interactive=False,
                       zoom=14,
                       lng=-68.3823549,
                       lat=44.3036906)
        Args:
            layers (list, optional): List of one or more of the following:

                - Layer: cartoframes Layer object for visualizing data from a
                  CARTO table. See `layer.Layer <#layer.Layer>`__ for all
                  styling options.
                - BaseMap: Basemap for contextualizng data layers. See
                  `layer.BaseMap <#layer.BaseMap>`__ for all styling options.
                - QueryLayer: Layer from an arbitrary query. See
                  `layer.QueryLayer <#layer.QueryLayer>`__ for all styling
                  options.

            interactive (bool, optional): Defaults to ``True`` to show an
                interactive slippy map. Setting to ``False`` creates a static
                map.
            zoom (int, optional): Zoom level of map. Acceptable values are
                usually in the range 0 to 19. 0 has the entire earth on a
                single tile (256px square). Zoom 19 is the size of a city
                block. Must be used in conjunction with ``lng`` and ``lat``.
                Defaults to a view to have all data layers in view.
            lat (float, optional): Latitude value for the center of the map.
                Must be used in conjunction with ``zoom`` and ``lng``. Defaults
                to a view to have all data layers in view.
            lng (float, optional): Longitude value for the center of the map.
                Must be used in conjunction with ``zoom`` and ``lat``. Defaults
                to a view to have all data layers in view.
            size (tuple, optional): List of pixel dimensions for the map.
                Format is ``(width, height)``. Defaults to ``(800, 400)``.
            ax: matplotlib axis on which to draw the image. Only used when
                ``interactive`` is ``False``.

        Returns:
            IPython.display.HTML or matplotlib Axes: Interactive maps are
            rendered as HTML in an `iframe`, while static maps are returned as
            matplotlib Axes objects or IPython Image.
        """
        # TODO: add layers preprocessing method like
        #       layers = process_layers(layers)
        #       that uses up to layer limit value error
        if layers is None:
            layers = []
        elif not isinstance(layers, collections.Iterable):
            layers = [layers]
        else:
            layers = list(layers)

        if len(layers) > 8:
            raise ValueError('Map can have at most 8 layers')

        nullity = [zoom is None, lat is None, lng is None]
        if any(nullity) and not all(nullity):
            raise ValueError('Zoom, lat, and lng must all or none be provided')

        # When no layers are passed, set default zoom
        if ((len(layers) == 0 and zoom is None) or
                (len(layers) == 1 and layers[0].is_basemap)):
            [zoom, lat, lng] = [1, 0, 0]
        has_zoom = zoom is not None

        # Check for a time layer, if it exists move it to the front
        time_layers = [idx for idx, layer in enumerate(layers)
                       if not layer.is_basemap and layer.time]
        time_layer = layers[time_layers[0]] if len(time_layers) > 0 else None
        if len(time_layers) > 1:
            raise ValueError('Map can at most take 1 Layer with time '
                             'column/field')
        if time_layer:
            if not interactive:
                raise ValueError('Map cannot display a static image with a '
                                 'time column')
            layers.append(layers.pop(time_layers[0]))

        base_layers = [idx for idx, layer in enumerate(layers)
                       if layer.is_basemap]

        # Check basemaps, add one if none exist
        if len(base_layers) > 1:
            raise ValueError('Map can at most take one BaseMap layer')
        elif len(base_layers) == 1:
            layers.insert(0, layers.pop(base_layers[0]))
            if layers[0].is_basic() and layers[0].labels == 'front':
                if time_layers:
                    warn('Basemap labels on top are not currently supported '
                         'for animated maps')
                else:
                    layers.append(BaseMap(layers[0].source,
                                          labels=layers[0].labels,
                                          only_labels=True))
        elif not base_layers:
            # default basemap is dark with labels in back
            # labels will be changed if all geoms are non-point
            layers.insert(0, BaseMap())
            geoms = set()

        # Setup layers
        for idx, layer in enumerate(layers):
            if not layer.is_basemap:
                # get schema of style columns
                resp = self.sql_client.send('''
                    SELECT {cols}
                    FROM ({query}) AS _wrap
                    LIMIT 0
                '''.format(cols=','.join(layer.style_cols),
                           comma=',' if layer.style_cols else '',
                           query=layer.orig_query),
                   **DEFAULT_SQL_ARGS)
                self._debug_print(layer_fields=resp)
                for k, v in dict_items(resp['fields']):
                    layer.style_cols[k] = v['type']
                layer.geom_type = self._geom_type(layer)
                if not base_layers:
                    geoms.add(layer.geom_type)
                # update local style schema to help build proper defaults
            layer._setup(layers, idx)

        # set labels on top if there are no point geometries and a basemap
        #  is not specified
        if not base_layers and 'point' not in geoms:
            layers[0] = BaseMap(labels='front')

        # If basemap labels are on front, add labels layer
        basemap = layers[0]
        if basemap.is_basic() and basemap.labels == 'front':
            layers.append(BaseMap(basemap.source,
                                  labels=basemap.labels,
                                  only_labels=True))

        nb_layers = non_basemap_layers(layers)
        if time_layer and len(nb_layers) > 1:
            raise ValueError('Maps with a time element can only consist of a '
                             'time layer and a basemap. This constraint will '
                             'be removed in the future.')
        options = {'basemap_url': basemap.url}

        for idx, layer in enumerate(nb_layers):
            self._check_query(layer.query,
                              style_cols=layer.style_cols)
            options['cartocss_' + str(idx)] = layer.cartocss
            options['sql_' + str(idx)] = layer.query

        params = {
            'config': json.dumps(options),
            'anti_cache': random.random(),
        }

        if has_zoom:
            params.update({'zoom': zoom, 'lat': lat, 'lon': lng})
            options.update({'zoom': zoom, 'lat': lat, 'lng': lng})
        else:
            bounds = self._get_bounds(nb_layers)
            options.update(bounds)
            bbox = '{west},{south},{east},{north}'.format(**bounds)
            params.update(dict(bbox=bbox))

        map_name = self._send_map_template(layers, has_zoom=has_zoom)
        api_url = join_url((self.creds.base_url(), 'api/v1/map', ))

        static_url = ('{api_url}/static/named/{map_name}'
                      '/{width}/{height}.png?{params}').format(
                          api_url=api_url,
                          map_name=map_name,
                          width=size[0],
                          height=size[1],
                          params=urlencode(params))

        html = '<img src="{url}" />'.format(url=static_url)

        # TODO: write this as a private method
        if interactive:
            netloc = urlparse(self.creds.base_url()).netloc
            domain = 'carto.com' if netloc.endswith('.carto.com') else netloc

            def safe_quotes(text, escape_single_quotes=False):
                """htmlify string"""
                if isinstance(text, str):
                    safe_text = text.replace('"', "&quot;")
                    if escape_single_quotes:
                        safe_text = safe_text.replace("'", "&#92;'")
                    return safe_text.replace('True', 'true')
                return text

            config = {
                'user_name': self.creds.username(),
                'maps_api_template': self.creds.base_url(),
                'sql_api_template': self.creds.base_url(),
                'tiler_protocol': 'https',
                'tiler_domain': domain,
                'tiler_port': '80',
                'type': 'torque' if time_layer else 'namedmap',
                'named_map': {
                    'name': map_name,
                    'params': {
                        k: safe_quotes(v, escape_single_quotes=True)
                        for k, v in dict_items(options)
                    },
                },
            }

            map_options = {
                'filter': ['http', 'mapnik', 'torque'],
                'https': True,
            }

            if time_layer:
                # get turbo-carto processed cartocss
                resp = self._auth_send(
                        'api/v1/map/named/{}'.format(map_name),
                        'POST',
                        data=params['config'],
                        headers={'Content-Type': 'application/json'})

                # check if errors in cartocss (already turbo-carto processed)
                if 'errors' not in resp:
                    # replace previous cartocss with turbo-carto processed
                    #  version
                    layer.cartocss = (resp['metadata']
                                          ['layers']
                                          [1]
                                          ['meta']
                                          ['cartocss'])
                config.update({
                    'order': 1,
                    'options': {
                        'query': time_layer.query,
                        'user_name': self.creds.username(),
                        'tile_style': layer.cartocss
                    }
                })
                config['named_map'].update({
                    'layers': [{
                        'layer_name': 't',
                    }],
                })
                map_options.update({
                    'time_slider': True,
                    'loop': True,
                })
            bounds = [] if has_zoom else [[options['north'], options['east']],
                                          [options['south'], options['west']]]

            content = self._get_iframe_srcdoc(config=config,
                                              bounds=bounds,
                                              options=options,
                                              map_options=map_options)

            img_html = html
            html = (
                '<iframe srcdoc="{content}" width={width} height={height}>'
                '  Preview image: {img_html}'
                '</iframe>'
            ).format(content=safe_quotes(content),
                     width=size[0],
                     height=size[1],
                     img_html=img_html)
            return IPython.display.HTML(html)
        elif HAS_MATPLOTLIB:
            raw_data = mpi.imread(static_url, format='png')
            if ax is None:
                dpi = mpi.rcParams['figure.dpi']
                mpl_size = (size[0] / dpi, size[1] / dpi)
                fig = plt.figure(figsize=mpl_size, dpi=dpi, frameon=False)
                fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
                ax = plt.gca()
            ax.imshow(raw_data)
            ax.axis('off')
            return ax
        else:
            return IPython.display.Image(url=static_url,
                                         embed=True,
                                         format='png',
                                         width=size[0],
                                         height=size[1],
                                         metadata=dict(origin_url=static_url))

    def _geom_type(self, layer):
        """gets geometry type(s) of specified layer"""
        resp = self.sql_client.send('''
            SELECT
                CASE WHEN ST_GeometryType(the_geom) in ('ST_Point',
                                                        'ST_MultiPoint')
                     THEN 'point'
                     WHEN ST_GeometryType(the_geom) in ('ST_LineString',
                                                        'ST_MultiLineString')
                     THEN 'line'
                     WHEN ST_GeometryType(the_geom) in ('ST_Polygon',
                                                        'ST_MultiPolygon')
                     THEN 'polygon'
                     ELSE null END AS geom_type,
                count(*) as cnt
            FROM ({query}) AS _wrap
            WHERE the_geom IS NOT NULL
            GROUP BY 1
            ORDER BY 2 DESC
        '''.format(query=layer.orig_query),
            **DEFAULT_SQL_ARGS)
        if len(resp['rows']) > 1:
            warn('There are multiple geometry types in {query}: '
                 '{geoms}. Styling by `{common_geom}`, the most common'.format(
                    query=layer.orig_query,
                    geoms=','.join(g['geom_type'] for g in resp['rows']),
                    common_geom=resp['rows'][0]['geom_type']))
        return resp['rows'][0]['geom_type']

    def data_boundaries(self, df=None, table_name=None):
        """Not currently implemented"""
        pass

    def data_discovery(self, keywords=None, regex=None, time=None,
                       boundary=None):
        """Not currently implemented"""
        pass

    def data_augment(self, table_name, metadata):
        """Augment an existing CARTO table with `Data Observatory
        <https://carto.com/data-observatory>`__ measures. See the full `Data
        Observatory catalog
        <https://cartodb.github.io/bigmetadata/index.html>`__ for all available
        measures. The result of this operation is:

        1. It updates `table_name` by adding columns from the Data Observatory
        2. It returns a pandas DataFrame representation of that newly augmented
           table.

        Note:
            This method alters `table_name` in the user's CARTO database by
            adding additional columns. To avoid this, create a copy of the
            table first and use the new copy instead.

        Example:
            Add new measures to a CARTO table and pass it to a pandas
            DataFrame. Using the "Median Household Income in the past 12
            months" measure from the `Data Observatory Catalog
            <https://cartodb.github.io/bigmetadata/united_states/income.html#median-household-income-in-the-past-12-months>`__.
            ::

                import cartoframes
                cc = cartoframes.CartoContext(BASEURL, APIKEY)
                median_income = [{'numer_id': 'us.census.acs.B19013001',
                                  'geom_id': 'us.census.tiger.block_group',
                                  'numer_timespan': '2011 - 2015'}]
                df = cc.data_augment('transaction_events',
                                     median_income)

        Args:
            table_name (str): Name of table on CARTO account that Data
                Observatory measures are to be added to.
            metadata (list of dicts): List of all measures to add to
                `table_name`. Each `dict` has the following keys:

                - `numer_id` (str): The identifier for the desired measurement
                - `geom_id` (str, optional): Identifier for a desired
                  geographic boundary level to use when calculating measures.
                  Will be automatically assigned if undefined
                - `normalization` (str, optional): The desired normalization.
                  One of 'area', 'prenormalized', or 'denominated'. 'Area' will
                  normalize the measure per square kilometer, 'prenormalized'
                  will return the original value, and 'denominated' will
                  normalize by a denominator.
                - `denom_id` (str, optional): Measure ID from DO catalog
                - `numer_timespan` (str, optional): The desired timespan for
                  the measurement. Defaults to most recent timespan available
                  if left unspecified.
                - `geom_timespan` (str, optional): The desired timespan for the
                  geometry. Defaults to timespan matching `numer_timespan` if
                  left unspecified.
                - `target_area` (str, optional): Instead of aiming to have
                  `target_geoms` in the area of the geometry passed as extent,
                  fill this area. Unit is square degrees WGS84. Set this to
                  `0` if you want to use the smallest source geometry for this
                  element of metadata, for example if you're passing in points.
                - `target_geoms` (str, optional): Override global
                  `target_geoms` for this element of metadata
                - `max_timespan_rank` (str, optional): Override global
                  `max_timespan_rank` for this element of metadata
                - `max_score_rank` (str, optional): Override global
                  `max_score_rank` for this element of metadata

        Returns:
            pandas.DataFrame: A DataFrame representation of `table_name` which
            has new columns for each measure in `metadata`.
        """

        try:
            with open(os.path.join(os.path.dirname(__file__),
                                   'assets/data_obs_augment.sql'), 'r') as f:
                augment_functions = f.read()
            self.sql_client.send(augment_functions, do_post=False)
        except Exception as err:
            raise CartoException("Could not install `obs_augment_table` onto "
                                 "user account ({})".format(err))

        # augment with data observatory metadata
        augment_query = '''
            select obs_augment_table('{username}.{tablename}',
                                     '{cols_meta}');
        '''.format(username=self.creds.username(),
                   tablename=table_name,
                   cols_meta=json.dumps(metadata))
        self.sql_client.send(augment_query, **DEFAULT_SQL_ARGS)

        # read full augmented table
        return self.read(table_name)

    def _auth_send(self, relative_path, http_method, **kwargs):
        self._debug_print(relative_path=relative_path,
                          http_method=http_method,
                          kwargs=kwargs)
        res = self.auth_client.send(relative_path, http_method, **kwargs)
        if isinstance(res.content, str):
            return json.loads(res.content)
        return json.loads(res.content.decode('utf-8'))

    def _check_query(self, query, style_cols=None):
        """Checks if query from Layer or QueryLayer is valid"""
        try:
            self.sql_client.send('''
                EXPLAIN
                SELECT
                  {style_cols}{comma}
                  the_geom, the_geom_webmercator
                FROM ({query}) _wrap;
                '''.format(query=query,
                           comma=',' if style_cols else '',
                           style_cols=(','.join(style_cols)
                                       if style_cols else '')),
                           do_post=False)
        except Exception as err:
            raise ValueError(('Layer query `{query}` and/or style column(s) '
                              '{cols} are not valid: {err}.'
                              '').format(query=query,
                                         cols=', '.join(['`{}`'.format(c)
                                                         for c in style_cols]),
                                         err=err))

    def _send_map_template(self, layers, has_zoom):
        map_name = get_map_name(layers, has_zoom=has_zoom)
        if map_name not in self._map_templates:
            resp = self._auth_send(
                    'api/v1/map/named', 'POST',
                    headers={'Content-Type': 'application/json'},
                    data=get_map_template(layers, has_zoom=has_zoom))
            # TODO: remove this after testing
            if 'errors' in resp:
                resp = self._auth_send(
                        'api/v1/map/named/{}'.format(map_name),
                        'PUT',
                        headers={'Content-Type': 'application/json'},
                        data=get_map_template(layers, has_zoom=has_zoom))

            self._map_templates[map_name] = True
        return map_name

    def _get_iframe_srcdoc(self, config, bounds, options, map_options):
        if not hasattr(self, '_srcdoc') or self._srcdoc is None:
            with open(os.path.join(os.path.dirname(__file__),
                                   'assets/cartoframes.html'), 'r') as f:
                self._srcdoc = f.read()

        return (self._srcdoc
                .replace('@@CONFIG@@', json.dumps(config))
                .replace('@@BOUNDS@@', json.dumps(bounds))
                .replace('@@OPTIONS@@', json.dumps(map_options))
                .replace('@@ZOOM@@', str(options.get('zoom', 3)))
                .replace('@@LAT@@', str(options.get('lat', 0)))
                .replace('@@LNG@@', str(options.get('lng', 0))))

    def _get_bounds(self, layers):
        """Return the bounds of all data layers involved in a cartoframes map.

        Args:
            layers (list): List of cartoframes layers. See `cartoframes.layers`
                for all types.

        Returns:
            dict: Dictionary of northern, southern, eastern, and western bounds
                of the superset of data layers. Keys are `north`, `south`,
                `east`, and `west`. Units are in WGS84.
        """
        extent_query = ('SELECT ST_EXTENT(the_geom) AS the_geom '
                        'FROM ({query}) AS t{idx}\n')
        union_query = 'UNION ALL\n'.join(
            [extent_query.format(query=layer.orig_query, idx=idx)
             for idx, layer in enumerate(layers)
             if not layer.is_basemap])

        extent = self.sql_client.send(
            '''
            SELECT
              ST_XMIN(ext) AS west,
              ST_YMIN(ext) AS south,
              ST_XMAX(ext) AS east,
              ST_YMAX(ext) AS north
            FROM (
                SELECT ST_Extent(the_geom) AS ext
                FROM ({union_query}) AS _wrap1
            ) AS _wrap2'''.format(union_query=union_query),
            do_post=False)

        return extent['rows'][0]

    def _debug_print(self, **kwargs):
        if self._verbose <= 0:
            return

        for key, value in dict_items(kwargs):
            if isinstance(value, requests.Response):
                str_value = ("status_code: {status_code}, "
                             "content: {content}").format(
                                 status_code=value.status_code,
                                 content=value.content)
            else:
                str_value = str(value)
            if self._verbose < 2 and len(str_value) > 300:
                str_value = '{}\n\n...\n\n{}'.format(str_value[:250],
                                                     str_value[-50:])
            print('{key}: {value}'.format(key=key,
                                          value=str_value))


def _add_encoded_geom(df, geom_col):
    """Add encoded geometry to DataFrame"""
    # None if not a GeoDataFrame
    is_geopandas = getattr(df, '_geometry_column_name', None)
    if is_geopandas is None and geom_col is None:
        warn('`encode_geom` works best with Geopandas '
             '(http://geopandas.org/) and/or shapely '
             '(https://pypi.python.org/pypi/Shapely).')
        geom_col = 'geometry' if 'geometry' in df.columns else None
        if geom_col is None:
            raise KeyError('Geometries were requested to be encoded '
                           'but a geometry column was not found in the '
                           'DataFrame.'.format(geom_col=geom_col))
    elif is_geopandas and geom_col:
        warn('Geometry column of the input DataFrame does not '
             'match the geometry column supplied. Using user-supplied '
             'column...\n'
             '\tGeopandas geometry column: {}\n'
             '\tSupplied `geom_col`: {}'.format(is_geopandas,
                                                geom_col))
    elif is_geopandas and geom_col is None:
        geom_col = is_geopandas
    # updates in place
    df['the_geom'] = df[geom_col].apply(_encode_geom)
    return None


def _encode_decode_decorator(func):
    """decorator for encoding and decoding geoms"""
    def wrapper(*args):
        """error catching"""
        try:
            processed_geom = func(*args)
            return processed_geom
        except ImportError as err:
            raise ImportError('The Python package `shapely` needs to be '
                              'installed to encode or decode geometries. '
                              '({})'.format(err))
    return wrapper


@_encode_decode_decorator
def _encode_geom(geom):
    """Encode geometries into hex-encoded wkb
    """
    from shapely import wkb
    if geom:
        return ba.hexlify(wkb.dumps(geom)).decode()
    return None


@_encode_decode_decorator
def _decode_geom(ewkb):
    """Decode encoded wkb into a shapely geometry
    """
    from shapely import wkb
    if ewkb:
        return wkb.loads(ba.unhexlify(ewkb))
    return None


def _dtypes2pg(dtype):
    """Returns equivalent PostgreSQL type for input `dtype`"""
    mapping = {
        'float64': 'numeric',
        'int64': 'numeric',
        'float32': 'numeric',
        'int32': 'numeric',
        'object': 'text',
        'bool': 'boolean',
        'datetime64[ns]': 'timestamp',
    }
    return mapping.get(str(dtype), 'text')


def _pg2dtypes(pgtype):
    """Returns equivalent dtype for input `pgtype`."""
    mapping = {
        'date': 'datetime64[ns]',
        'number': 'float64',
        'string': 'object',
        'boolean': 'bool',
        'geometry': 'object',
    }
    return mapping.get(str(pgtype), 'object')


def _df2pg_schema(dataframe, pgcolnames):
    """Print column names with PostgreSQL schema for the SELECT statement of
    a SQL query"""
    schema = ', '.join([
        'NULLIF("{col}", \'\')::{t} AS {col}'.format(col=c,
                                                     t=_dtypes2pg(t))
        for c, t in zip(pgcolnames, dataframe.dtypes)
        if c not in ('the_geom', 'the_geom_webmercator', 'cartodb_id')])
    if 'the_geom' in pgcolnames:
        return '"the_geom", ' + schema
    return schema


class BatchJobStatus(object):
    """Status of a write or query operation. Read more at `Batch SQL API docs
    <https://carto.com/docs/carto-engine/sql-api/batch-queries/>`__ about
    responses and how to interpret them.

    Example:

        Poll for a job's status if you've caught the :obj:`BatchJobStatus`
        instance.

        .. code:: python

            import time
            job = cc.write(df, 'new_table',
                           lnglat=('lng_col', 'lat_col'))
            while True:
                curr_status = job.status()['status']
                if curr_status in ('done', 'failed', 'canceled', 'unknown', ):
                    print(curr_status)
                    break
                time.sleep(5)

        Create a :obj:`BatchJobStatus` instance if you have a `job_id` output
        from a `cc.write` operation.

        .. code:: python

            >>> from cartoframes import CartoContext, BatchJobStatus
            >>> cc = CartoContext(username='...', api_key='...')
            >>> cc.write(df, 'new_table', lnglat=('lng', 'lat'))
            'BatchJobStatus(job_id='job-id-string', ...)'
            >>> batch_job = BatchJobStatus(cc, 'job-id-string')

    Attrs:
        job_id (str): Job ID of the Batch SQL API job
        last_status (str): Status of ``job_id`` job when last polled
        created_at (str): Time and date when job was created

    Args:
        carto_context (carto.CartoContext): CartoContext instance
        job (dict or str): If a dict, job status dict returned after sending
            a Batch SQL API request. If str, a Batch SQL API job id.
    """
    def __init__(self, carto_context, job):
        if isinstance(job, dict):
            self.job_id = job.get('job_id')
            self.last_status = job.get('status')
            self.created_at = job.get('created_at')
        elif isinstance(job, str):
            self.job_id = job
            self.last_status = None
            self.created_at = None

        self._batch_client = BatchSQLClient(carto_context.auth_client)

    def __repr__(self):
        return ('BatchJobStatus(job_id=\'{job_id}\', '
                'last_status=\'{status}\', '
                'created_at=\'{created_at}\')'.format(
                    job_id=self.job_id,
                    status=self.last_status,
                    created_at=self.created_at
                    )
                )

    def _set_status(self, curr_status):
        self.last_status = curr_status

    def get_status(self):
        """return current status of job"""
        return self.last_status

    def status(self):
        """Checks the current status of job ``job_id``

        Returns:
            dict: Status and time it was updated

        Warns:
            UserWarning: If the job failed, a warning is raised with
                information about the failure
        """
        resp = self._batch_client.read(self.job_id)
        if 'failed_reason' in resp:
            warn('Job failed: {}'.format(resp.get('failed_reason')))
        self._set_status(resp.get('status'))
        return dict(status=resp.get('status'),
                    updated_at=resp.get('updated_at'),
                    created_at=resp.get('created_at'))
