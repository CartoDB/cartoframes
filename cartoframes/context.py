"""CartoContext class for authentication with CARTO and high-level operations
such as reading tables from CARTO into dataframes, writing dataframes to CARTO
tables, and creating custom maps from dataframes and CARTO tables. Future
methods interact with CARTO's services like
`Data Observatory <https://carto.com/data-observatory>`__, and `routing,
geocoding, and isolines <https://carto.com/location-data-services/>`__.
"""
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

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
from carto.exceptions import CartoException

from .credentials import Credentials
from .utils import dict_items, normalize_colnames
from .layer import BaseMap
from .maps import non_basemap_layers, get_map_name, get_map_template

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


class CartoContext(object):
    """Manages connections with CARTO for data and map operations. Modeled
    after `SparkContext
    <https://jaceklaskowski.gitbooks.io/mastering-apache-spark/content/spark-sparkcontext.html>`__.

    Example:
        Create a CartoContext object::

            import cartoframes
            cc = cartoframes.CartoContext(BASEURL, APIKEY)

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
        res = self.sql_client.send('SHOW search_path')

        paths = [p.strip() for p in res['rows'][0]['search_path'].split(',')]
        # is an org user if first item is not `public`
        return paths[0] != 'public'

    def read(self, table_name, limit=None, index='cartodb_id',
             decode_geom=False):
        """Read tables from CARTO into pandas DataFrames.

        Example:
            .. code:: python

                import cartoframes
                cc = cartoframes.CartoContext(BASEURL, APIKEY)
                df = cc.read('acadia_biodiversity')

        Args:
            table_name (str): Name of table in user's CARTO account.
            limit (int, optional): Read only ``limit`` lines from
                ``table_name``. Defaults to `None`, which reads the full table.
            index (str, optional): Not currently in use.

        Returns:
            pandas.DataFrame: DataFrame representation of `table_name` from
            CARTO.
        """
        query = 'SELECT * FROM "{table_name}"'.format(table_name=table_name)
        if limit:
            if isinstance(limit, int) and (limit >= 0):
                query += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")

        return self.query(query, decode_geom=decode_geom)

    def write(self, df, table_name, temp_dir='/tmp', overwrite=False,
              lnglat=None, encode_geom=False, geom_col=None):
        """Write a DataFrame to a CARTO table.

        Example:
            .. code:: python

                cc.write(df, 'brooklyn_poverty', overwrite=True)

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

        Returns:
            None
        """
        if encode_geom:
            _add_encoded_geom(df, geom_col)

        if not overwrite:
            # error if table exists and user does not want to overwrite
            self._table_exists(table_name)
        pgcolnames = normalize_colnames(df.columns)
        if df.shape[0] > MAX_IMPORT_ROWS:
            # NOTE: schema is set using different method than in _set_schema
            final_table_name = self._send_batches(df, table_name, temp_dir,
                                                  geom_col, pgcolnames)
        else:
            final_table_name = self._send_dataframe(df, table_name, temp_dir,
                                                    geom_col, pgcolnames)
            self._set_schema(df, final_table_name, pgcolnames)

        # create geometry column from lat/longs if requested
        if lnglat:
            # TODO: make this a batch job if it is a large dataframe or move
            #       inside of _send_dataframe and/or batch
            tqdm.write('Creating geometry out of columns '
                       '`{lng}`/`{lat}`'.format(lng=lnglat[0],
                                                lat=lnglat[1]))
            self.sql_client.send('''
                UPDATE "{table_name}"
                SET the_geom = CDB_LatLng("{lat}"::numeric,
                                          "{lng}"::numeric)
            '''.format(table_name=final_table_name,
                       lng=lnglat[0],
                       lat=lnglat[1]))

        tqdm.write('Table successfully written to CARTO: '
                   '{base_url}dataset/{table_name}'.format(
                       base_url=self.creds.base_url(),
                       table_name=final_table_name))

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
                '''.format(table_name=table_name))
            raise NameError(
                'Table `{table_name}` already exists. '
                'Run with `overwrite=True` if you wish to replace the '
                'table.'.format(table_name=table_name))
        except CartoException as err:
            # If table doesn't exist, we get an error from the SQL API
            self._debug_print(err=err)
            return False

        return False

    def _send_batches(self, df, table_name, temp_dir, geom_col, pgcolnames):
        """Batch sending a dataframe

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

        Exceptions:
            * TODO: add more (Out of storage)
        """
        subtables = []
        # send dataframe chunks to carto
        for chunk_num, chunk in tqdm(df.groupby([i // MAX_IMPORT_ROWS
                                                 for i in range(df.shape[0])]),
                                     desc='Uploading in batches: '):
            temp_table = '{orig}_cartoframes_temp_{chunk}'.format(
                orig=table_name[:40],
                chunk=chunk_num)
            try:
                # send dataframe chunk, get new name if collision
                temp_table = self._send_dataframe(chunk, temp_table, temp_dir,
                                                  geom_col, pgcolnames)
            except CartoException as err:
                for table in subtables:
                    self.delete(table)
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
                    'DROP TABLE IF EXISTS {table};'.format(table=table)
                    for table in subtables)
            query = '''
                DROP TABLE IF EXISTS "{table_name}";
                CREATE TABLE "{table_name}" As {unioned_tables};
                ALTER TABLE {table_name} DROP COLUMN IF EXISTS cartodb_id;
                {drop_tables}
                SELECT CDB_CartoDBFYTable('{org}', '{table_name}');
                '''.format(table_name=table_name,
                           unioned_tables=unioned_tables,
                           org=(self.creds.username()
                                if self.is_org else 'public'),
                           drop_tables=drop_tables)
            self._debug_print(query=query)
            _ = self.sql_client.send(query)
        except CartoException as err:
            for table in subtables:
                self.delete(table)
            raise Exception('Failed to upload dataframe: {}'.format(err))

        return table_name

    def _send_dataframe(self, df, table_name, temp_dir, geom_col, pgcolnames):
        """Send a DataFrame to CARTO to be imported as a SQL table.

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
        df.drop(geom_col, axis=1, errors='ignore').to_csv(path_or_buf=tempfile,
                                                          na_rep='',
                                                          header=pgcolnames)

        with open(tempfile, 'rb') as f:
            res = self._auth_send('api/v1/imports', 'POST',
                                  files={'file': f},
                                  params={'type_guessing': 'false'},
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
            _ = self.sql_client.send(alter_query)
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
                        ALTER TABLE {dupe_table}
                        RENAME TO {orig_table};
                        '''.format(
                            orig_table=table_name,
                            dupe_table=import_job['table_name']))

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
            query (str): Query to run against CARTO user database.
            table_name (str, optional): If set, this will create a new
                table in the user's CARTO account that is the result of the
                query. Defaults to None (no table created).
        Returns:
            pandas.DataFrame: DataFrame representation of query supplied.
            Pandas data types are inferred from PostgreSQL data types.
            In the case of PostgreSQL date types, the data type 'object' is
            used.
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

            create_table_res = self.sql_client.send(create_table_query)
            self._debug_print(create_table_res=create_table_res)

            new_table_name = create_table_res['rows'][0]['cdb_cartodbfytable']
            self._debug_print(new_table_name=new_table_name)

            select_res = self.sql_client.send(
                'SELECT * FROM {table_name}'.format(table_name=new_table_name))
        else:
            select_res = self.sql_client.send(query)

        self._debug_print(select_res=select_res)

        fields = select_res['fields']
        if not len(fields):
            return pd.DataFrame()

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
            IPython.display.HTML: Interactive maps are rendered in an
            ``iframe``, while static maps are rendered in ``img`` tags.
        """
        # TODO: add layers preprocessing method like
        #       layers = process_layers(layers)
        #       that uses up to layer limit value error
        if not hasattr(IPython, 'display'):
            raise NotImplementedError('Nope, cannot display maps at the '
                                      'command line.')

        if layers is None:
            layers = []
        elif not isinstance(layers, collections.Iterable):
            layers = [layers]
        else:
            layers = list(layers)

        if len(layers) > 8:
            raise ValueError('map can have at most 8 layers')

        nullity = [zoom is None, lat is None, lng is None]
        if any(nullity) and not all(nullity):
            raise ValueError('zoom, lat, and lng must all or none be provided')

        # When no layers are passed, set default zoom
        if ((len(layers) == 0 and zoom is None) or
                (len(layers) == 1 and layers[0].is_basemap)):
            [zoom, lat, lng] = [3, 38, -99]
        has_zoom = zoom is not None

        # Check basemaps, add one if none exist
        base_layers = [idx for idx, layer in enumerate(layers)
                       if layer.is_basemap]
        if len(base_layers) > 1:
            raise ValueError('map can at most take 1 BaseMap layer')
        if len(base_layers) > 0:
            layers.insert(0, layers.pop(base_layers[0]))
        else:
            layers.insert(0, BaseMap())

        # Check for a time layer, if it exists move it to the front
        time_layers = [idx for idx, layer in enumerate(layers)
                       if not layer.is_basemap and layer.time]
        time_layer = layers[time_layers[0]] if len(time_layers) > 0 else None
        if len(time_layers) > 1:
            raise ValueError('Map can at most take 1 Layer with time '
                             'column/field')
        if time_layer:
            raise NotImplementedError('Animated maps are not yet supported')
            if not interactive:
                raise ValueError('map cannot display a static image with a '
                                 'time_column')
            layers.append(layers.pop(time_layers[0]))

        # If basemap labels are on front, add labels layer
        basemap = layers[0]
        if basemap.is_basic() and basemap.labels == 'front':
            layers.append(BaseMap(basemap.source,
                                  labels=basemap.labels,
                                  only_labels=True))

        # Setup layers
        for idx, layer in enumerate(layers):
            layer._setup(layers, idx)

        nb_layers = non_basemap_layers(layers)
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
            options.update(self._get_bounds(nb_layers))

        map_name = self._send_map_template(layers, has_zoom=has_zoom)
        api_url = '{base_url}api/v1/map'.format(base_url=self.creds.base_url())

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
                'maps_api_template': self.creds.base_url()[:-1],
                'sql_api_template': self.creds.base_url()[:-1],
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
                config.update({
                    'order': 1,
                    'options': {
                        'query': time_layer.query,
                        'user_name': self.creds.username(),
                        'tile_style': time_layer.torque_cartocss,
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
            self.sql_client.send(augment_functions)
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
        _ = self.sql_client.send(augment_query)

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
                                       if style_cols else '')))
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
            try:
                self._auth_send('api/v1/map/named', 'POST',
                                headers={'Content-Type': 'application/json'},
                                data=get_map_template(layers,
                                                      has_zoom=has_zoom))
            except ValueError('map already exists'):
                pass

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
            [extent_query.format(query=layer.query, idx=idx)
             for idx, layer in enumerate(layers)
             if not layer.is_basemap])

        extent = self.sql_client.send('''
                       SELECT
                         ST_XMIN(ext) AS west,
                         ST_YMIN(ext) AS south,
                         ST_XMAX(ext) AS east,
                         ST_YMAX(ext) AS north
                       FROM (
                           SELECT ST_Extent(the_geom) AS ext
                           FROM ({union_query}) AS _wrap1
                       ) AS _wrap2
                            '''.format(union_query=union_query))

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
        'datetime64[ns]': 'date',
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
