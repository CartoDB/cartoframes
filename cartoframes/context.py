"""
This class is the workhorse of CARTOframes by providing all functionality related to
data access to CARTO, map creation, and Data Observatory functionality.
"""
from __future__ import absolute_import
import json
import os
import random
import sys
import collections
from warnings import warn

import requests
from IPython.display import HTML, Image
import pandas as pd
from tqdm import tqdm
from appdirs import user_cache_dir

from carto.auth import APIKeyAuthClient, AuthAPIClient
from carto.sql import SQLClient, BatchSQLClient, CopySQLClient
from carto.exceptions import CartoException
from carto.datasets import DatasetManager
from pyrestcli.exceptions import NotFoundException

from .credentials import Credentials
from .dataobs import get_countrytag
from . import utils
from .layer import BaseMap, AbstractLayer
from .maps import (non_basemap_layers, get_map_name,
                   get_map_template, top_basemap_layer_url)
from .analysis import Table
from .__version__ import __version__
from .columns import dtypes, date_columns_names
from .dataset import Dataset, recursive_read, _decode_geom, get_columns

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
MAX_ROWS_LNGLAT = 1000

# Cache directory for temporary data operations
CACHE_DIR = user_cache_dir('cartoframes')

# cartoframes version
DEFAULT_SQL_ARGS = dict(do_post=False)

# avoid _lock issue: https://github.com/tqdm/tqdm/issues/457
tqdm(disable=True, total=0)  # initialise internal lock


class CartoContext(object):
    """CartoContext class for authentication with CARTO and high-level
    operations such as reading tables from CARTO into dataframes, writing
    dataframes to CARTO tables, creating custom maps from dataframes and CARTO
    tables, and augmenting data using CARTO's `Data Observatory
    <https://carto.com/data-observatory>`__. Future methods will interact with
    CARTO's services like `routing, geocoding, and isolines
    <https://carto.com/location-data-services/>`__, PostGIS backend for spatial
    processing, and much more.

    Manages connections with CARTO for data and map operations. Modeled
    after `SparkContext
    <http://spark.apache.org/docs/2.1.0/api/python/pyspark.html#pyspark.SparkContext>`__.

    There are two ways of authenticating against a CARTO account:

      1. Setting the `base_url` and `api_key` directly in
         :py:class:`CartoContext`. This method is easier.::

            cc = CartoContext(
                base_url='https://eschbacher.carto.com',
                api_key='abcdefg')

      2. By passing a :py:class:`Credentials
         <cartoframes.credentials.Credentials>` instance in
         :py:class:`CartoContext <cartoframes.context.CartoContext>`'s
         :py:attr:`creds <cartoframes.credentials.Credentials.creds>`
         keyword argument. This method is more flexible.::

            from cartoframes import Credentials
            creds = Credentials(username='eschbacher', key='abcdefg')
            cc = CartoContext(creds=creds)

    Attributes:
        creds (:py:class:`Credentials <cartoframes.credentials.Credentials>`):
          :py:class:`Credentials <cartoframes.credentials.Credentials>`
          instance

    Args:
        base_url (str): Base URL of CARTO user account. Cloud-based accounts
            should use the form ``https://{username}.carto.com`` (e.g.,
            https://eschbacher.carto.com for user ``eschbacher``) whether on
            a personal or multi-user account. On-premises installation users
            should ask their admin.
        api_key (str): CARTO API key.
        creds (:py:class:`Credentials <cartoframes.credentials.Credentials>`):
          A :py:class:`Credentials <cartoframes.credentials.Credentials>`
          instance can be used in place of a `base_url`/`api_key` combination.
        session (requests.Session, optional): requests session. See `requests
            documentation
            <http://docs.python-requests.org/en/master/user/advanced/>`__
            for more information.
        verbose (bool, optional): Output underlying process states (True), or
            suppress (False, default)

    Returns:
        :py:class:`CartoContext <cartoframes.context.CartoContext>`: A
        CartoContext object that is authenticated against the user's CARTO
        account.

    Example:

        Create a :py:class:`CartoContext` object for a cloud-based CARTO
        account.

        .. code::

            import cartoframes
            # if on prem, format is '{host}/user/{username}'
            BASEURL = 'https://{}.carto.com/'.format('your carto username')
            APIKEY = 'your carto api key'
            cc = cartoframes.CartoContext(BASEURL, APIKEY)

    Tip:

        If using cartoframes with an `on premises CARTO installation
        <https://carto.com/developers/on-premises/guides/builder/basics/>`__,
        sometimes it is necessary to disable SSL verification depending on your
        system configuration. You can do this using a `requests Session
        <http://docs.python-requests.org/en/master/user/advanced/#session-objects>`__
        object as follows:

        .. code::

            import cartoframes
            from requests import Session
            session = Session()
            session.verify = False

            # on prem host (e.g., an IP address)
            onprem_host = 'your on prem carto host'

            cc = cartoframes.CartoContext(
                base_url='{host}/user/{user}'.format(
                    host=onprem_host,
                    user='your carto username'),
                api_key='your carto api key',
                session=session
            )

    """

    def __init__(self, base_url=None, api_key=None, creds=None, session=None,
                 verbose=0):

        self.creds = Credentials(creds=creds, key=api_key, base_url=base_url)
        self.auth_client = APIKeyAuthClient(
            base_url=self.creds.base_url(),
            api_key=self.creds.key(),
            session=session,
            client_id='cartoframes_{}'.format(__version__),
            user_agent='cartoframes_{}'.format(__version__)
        )
        self.auth_api_client = AuthAPIClient(
            base_url=self.creds.base_url(),
            api_key=self.creds.key(),
            session=session
        )
        self.sql_client = SQLClient(self.auth_client)
        self.copy_client = CopySQLClient(self.auth_client)
        self.batch_sql_client = BatchSQLClient(self.auth_client)
        self.creds.username(self.auth_client.username)
        self._is_authenticated()
        self.is_org = self._is_org_user()

        self._map_templates = {}
        self._srcdoc = None
        self._verbose = verbose

    def _is_authenticated(self):
        """Checks if credentials allow for authenticated carto access"""
        if not self.auth_api_client.is_valid_api_key():
            raise CartoException(
                'Cannot authenticate user `{}`. Check credentials.'.format(
                    self.creds.username()))

    def _is_org_user(self):
        """Report whether user is in a multiuser CARTO organization or not"""
        res = self.sql_client.send("select unnest(current_schemas('f'))",
                                   **DEFAULT_SQL_ARGS)
        # is an org user if first item is not `public`
        return res['rows'][0]['unnest'] != 'public'

    def get_default_schema(self):
        return 'public' if not self.is_org else self.creds.username()

    def read(self, table_name, limit=None, decode_geom=False, shared_user=None, retry_times=3):
        """Read a table from CARTO into a pandas DataFrames. Column types are inferred from database types, to
          avoid problems with integer columns with NA or null values, they are automatically retrieved as float64

        Args:
            table_name (str): Name of table in user's CARTO account.
            limit (int, optional): Read only `limit` lines from
                `table_name`. Defaults to ``None``, which reads the full table.
            decode_geom (bool, optional): Decodes CARTO's geometries into a
              `Shapely <https://github.com/Toblerity/Shapely>`__
              object that can be used, for example, in `GeoPandas
              <http://geopandas.org/>`__.
            shared_user (str, optional): If a table has been shared with you,
              specify the user name (schema) who shared it.
            retry_times (int, optional): If the read call is rate limited,
              number of retries to be made

        Returns:
            pandas.DataFrame: DataFrame representation of `table_name` from
            CARTO.

        Example:
            .. code:: python

                import cartoframes
                cc = cartoframes.CartoContext(BASEURL, APIKEY)
                df = cc.read('acadia_biodiversity')
        """
        # choose schema (default user - org or standalone - or shared)
        schema = 'public' if not self.is_org else (
            shared_user or self.creds.username())

        dataset = Dataset.from_table(table_name, schema=schema, context=self)
        return dataset.download(limit, decode_geom, retry_times)

    @utils.temp_ignore_warnings
    def tables(self):
        """List all tables in user's CARTO account

        Returns:
            :obj:`list` of :py:class:`Table <cartoframes.analysis.Table>`

        """
        datasets = DatasetManager(self.auth_client).filter(
            show_table_size_and_row_count='false',
            show_table='false',
            show_stats='false',
            show_likes='false',
            show_liked='false',
            show_permission='false',
            show_uses_builder_features='false',
            show_synchronization='false',
            load_totals='false')
        return [Table.from_dataset(d) for d in datasets]

    def write(self, df, table_name, temp_dir=CACHE_DIR, overwrite=False,
              lnglat=None, encode_geom=False, geom_col=None, **kwargs):
        """Write a DataFrame to a CARTO table.

        Examples:
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

        .. warning:: datetime64[ns] column will lose precision sending a dataframe to CARTO
                     because postgresql has millisecond resolution while pandas does nanoseconds

        Args:
            df (pandas.DataFrame): DataFrame to write to ``table_name`` in user
                CARTO account
            table_name (str): Table to write ``df`` to in CARTO.
            temp_dir (str, optional): Directory for temporary storage of data
                that is sent to CARTO. Defaults are defined by `appdirs
                <https://github.com/ActiveState/appdirs/blob/master/README.rst>`__.
            overwrite (bool, optional): Behavior for overwriting ``table_name``
                if it exits on CARTO. Defaults to ``False``.
            lnglat (tuple, optional): lng/lat pair that can be used for
                creating a geometry on CARTO. Defaults to ``None``. In some
                cases, geometry will be created without specifying this. See
                CARTO's `Import API
                <https://carto.com/developers/import-api/reference/#tag/Standard-Tables>`__
                for more information.
            encode_geom (bool, optional): Whether to write `geom_col` to CARTO
                as `the_geom`.
            geom_col (str, optional): The name of the column where geometry
                information is stored. Used in conjunction with `encode_geom`.
            **kwargs: Keyword arguments to control write operations. Options
                are:

                - `compression` to set compression for files sent to CARTO.
                  This will cause write speedups depending on the dataset.
                  Options are ``None`` (no compression, default) or ``gzip``.
                - Some arguments from CARTO's Import API. See the `params
                  listed in the documentation
                  <https://carto.com/developers/import-api/reference/#tag/Standard-Tables>`__
                  for more information. For example, when using
                  `content_guessing='true'`, a column named 'countries' with
                  country names will be used to generate polygons for each
                  country. Another use is setting the privacy of a dataset. To
                  avoid unintended consequences, avoid `file`, `url`, and other
                  similar arguments.

        Returns:
            :py:class:`Dataset <cartoframes.datasets.Dataset>`

        .. note::
            DataFrame indexes are changed to ordinary columns. CARTO creates
            an index called `cartodb_id` for every table that runs from 1 to
            the length of the DataFrame.
        """  # noqa
        tqdm.write('Params: encode_geom, geom_col and everything in kwargs are deprecated and not being used any more')
        dataset = Dataset.from_dataframe(df)

        if_exists = Dataset.FAIL
        if overwrite:
            if_exists = Dataset.REPLACE

        dataset = dataset.upload(with_lnglat=lnglat, if_exists=if_exists, table_name=table_name, context=self)

        tqdm.write('Table successfully written to CARTO: {table_url}'.format(
            table_url=utils.join_url(self.creds.base_url(),
                                     'dataset',
                                     dataset.table_name)))

        return dataset

    @utils.temp_ignore_warnings
    def _get_privacy(self, table_name):
        """gets current privacy of a table"""
        ds_manager = DatasetManager(self.auth_client)
        try:
            dataset = ds_manager.get(table_name)
            return dataset.privacy.lower()
        except NotFoundException:
            return None

    @utils.temp_ignore_warnings
    def _update_privacy(self, table_name, privacy):
        """Updates the privacy of a dataset"""
        ds_manager = DatasetManager(self.auth_client)
        dataset = ds_manager.get(table_name)
        dataset.privacy = privacy
        dataset.save()

    def delete(self, table_name):
        """Delete a table in user's CARTO account.

        Args:
            table_name (str): Name of table to delete

        Returns:
            bool: `True` if table is removed

        """
        dataset = Dataset.from_table(table_name, context=self)
        deleted = dataset.delete()
        if deleted:
            return deleted

        raise CartoException('''The table `{}` doesn't exist'''.format(table_name))

    def _check_import(self, import_id):
        """Check the status of an Import API job"""

        res = self._auth_send('api/v1/imports/{}'.format(import_id),
                              'GET')
        return res

    def _handle_import(self, import_job, table_name):
        """Handle state of import job"""
        if import_job['state'] == 'failure':
            if import_job['error_code'] == 8001:
                raise CartoException(
                    'Over CARTO account storage limit for user `{}`. Try '
                    'subsetting your DataFrame or dropping columns to reduce '
                    'the data size.'.format(self.creds.username())
                )
            elif import_job['error_code'] == 6668:
                raise CartoException(
                    'Too many rows in DataFrame. Try subsetting '
                    'DataFrame before writing to CARTO.'
                )
            else:
                raise CartoException(
                    'Error code: `{}`. See CARTO Import API error '
                    'documentation for more information: '
                    'https://carto.com/developers/import-api/support/'
                    'import-errors/'.format(import_job['error_code'])
                )
        elif import_job['state'] == 'complete':
            import_job_table_name = import_job['table_name']
            self._debug_print(final_table=import_job_table_name)
            if import_job_table_name != table_name:
                try:
                    res = self.sql_client.send(
                        utils.minify_sql((
                            'DROP TABLE IF EXISTS {orig_table};',
                            'ALTER TABLE {dupe_table} RENAME TO {orig_table};',
                            'SELECT CDB_TableMetadataTouch(',
                            '           \'{orig_table}\'::regclass);',
                        )).format(
                            orig_table=table_name,
                            dupe_table=import_job_table_name),
                        do_post=False)

                    self._debug_print(res=res)
                except Exception as err:
                    self._debug_print(err=err)
                    raise Exception(
                        'Cannot overwrite table `{table_name}` ({err}). '
                        'DataFrame was written to `{new_table}` '
                        'instead.'.format(
                            table_name=table_name,
                            err=err,
                            new_table=import_job_table_name)
                    )
                finally:
                    self.delete(import_job_table_name)
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

    def fetch(self, query, decode_geom=False):
        """Pull the result from an arbitrary SELECT SQL query from a CARTO account
        into a pandas DataFrame.

        Args:
            query (str): SELECT query to run against CARTO user database. This data
              will then be converted into a pandas DataFrame.
            decode_geom (bool, optional): Decodes CARTO's geometries into a
              `Shapely <https://github.com/Toblerity/Shapely>`__
              object that can be used, for example, in `GeoPandas
              <http://geopandas.org/>`__.

        Returns:
            pandas.DataFrame: DataFrame representation of query supplied.
            Pandas data types are inferred from PostgreSQL data types.
            In the case of PostgreSQL date types, dates are attempted to be
            converted, but on failure a data type 'object' is used.

        Examples:
            This query gets the 10 highest values from a table and
            returns a dataframe.

            .. code:: python

                topten_df = cc.query(
                    '''
                      SELECT * FROM
                      my_table
                      ORDER BY value_column DESC
                      LIMIT 10
                    '''
                )

            This query joins points to polygons based on intersection, and
            aggregates by summing the values of the points in each polygon. The
            query returns a dataframe, with a geometry column that contains
            polygons.

            .. code:: python

                points_aggregated_to_polygons = cc.query(
                    '''
                      SELECT polygons.*, sum(points.values)
                      FROM polygons JOIN points
                      ON ST_Intersects(points.the_geom, polygons.the_geom)
                      GROUP BY polygons.the_geom, polygons.cartodb_id
                    ''',
                    decode_geom=True
                )

        """
        copy_query = 'COPY ({query}) TO stdout WITH (FORMAT csv, HEADER true)'.format(query=query)
        result = recursive_read(self, copy_query)

        query_columns = get_columns(self, query)
        df_types = dtypes(query_columns, exclude_dates=True, exclude_the_geom=True)
        date_column_names = date_columns_names(query_columns)

        df = pd.read_csv(result, dtype=df_types,
                         parse_dates=date_column_names,
                         true_values=['t'],
                         false_values=['f'],
                         index_col='cartodb_id' if 'cartodb_id' in df_types else False,
                         converters={'the_geom': lambda x: _decode_geom(x) if decode_geom else x})

        if decode_geom:
            df.rename({'the_geom': 'geometry'}, axis='columns', inplace=True)

        return df

    def execute(self, query):
        """Runs an arbitrary query to a CARTO account.

           This method is specially useful for queries that do not return any data and just
           perform a database operation like:

             - INSERT, UPDATE, DROP, CREATE, ALTER, stored procedures, etc.

           Queries are run using a `Batch SQL API job
           <https://carto.com/developers/sql-api/guides/batch-queries/>`__
           in the user account

           The execution of the queries is asynchronous but this method automatically
           waits for its completion (or failure). The `job_id` of the Batch SQL API job
           will be printed. In case there's any issue you can contact the CARTO support team
           specifying that `job_id`.

        Args:
            query (str): An SQL query to run against CARTO user database.

        Returns:
            None

        Raises:
            CartoException: If the query fails to execute

        Examples:

            Drops `my_table`

            .. code:: python

                cc.execute(
                    '''
                      DROP TABLE my_table
                    '''
                )

            Updates the column `my_column` in the table `my_table`

            .. code:: python

                cc.query(
                    '''
                      UPDATE my_table SET my_column = 1
                    '''
                )

        """
        self.batch_sql_client.create_and_wait_for_completion(query)

    def query(self, query, table_name=None, decode_geom=False, is_select=None):
        """Pull the result from an arbitrary SQL SELECT query from a CARTO account
        into a pandas DataFrame. This is the default behavior, when `is_select=True`

        Can also be used to perform database operations (creating/dropping tables,
        adding columns, updates, etc.). In this case, you have to explicitly
        specify `is_select=False`

        This method is a helper for the `CartoContext.fetch` and `CartoContext.execute`
        methods. We strongly encourage you to use any of those methods depending on the
        type of query you want to run. If you want to get the results of a `SELECT` query
        into a pandas DataFrame, then use `CartoContext.fetch`. For any other query that
        performs an operation into the CARTO database, use `CartoContext.execute`

        Args:
            query (str): Query to run against CARTO user database. This data
              will then be converted into a pandas DataFrame.
            table_name (str, optional): If set (and `is_select=True`), this will create a new
              table in the user's CARTO account that is the result of the SELECT
              query provided. Defaults to None (no table created).
            decode_geom (bool, optional): Decodes CARTO's geometries into a
              `Shapely <https://github.com/Toblerity/Shapely>`__
              object that can be used, for example, in `GeoPandas
              <http://geopandas.org/>`__. It only works for SELECT queries when `is_select=True`
            is_select (bool, optional): This argument has to be set depending on the query
              performed. True for SELECT queries, False for any other query.
              For the case of a SELECT SQL query (`is_select=True`) the result will be stored into a
              pandas DataFrame.
              When an arbitrary SQL query (`is_select=False`) it will perform a database
              operation (UPDATE, DROP, INSERT, etc.)
              By default `is_select=None` that means that the method will return a dataframe if
              the `query` starts with a `select` clause, otherwise it will just execute the query
              and return `None`

        Returns:
            pandas.DataFrame: When `is_select=True` and the query is actually a SELECT query
            this method returns a pandas DataFrame representation of query supplied otherwise
            returns None.
            Pandas data types are inferred from PostgreSQL data types.
            In the case of PostgreSQL date types, dates are attempted to be
            converted, but on failure a data type 'object' is used.

        Raises:
            CartoException: If there's any error when executing the query

        Examples:
            Query a table in CARTO and write a new table that is result of
            query. This query gets the 10 highest values from a table and
            returns a dataframe, as well as creating a new table called
            'top_ten' in the CARTO account.

            .. code:: python

                topten_df = cc.query(
                    '''
                      SELECT * FROM
                      my_table
                      ORDER BY value_column DESC
                      LIMIT 10
                    ''',
                    table_name='top_ten'
                )

            This query joins points to polygons based on intersection, and
            aggregates by summing the values of the points in each polygon. The
            query returns a dataframe, with a geometry column that contains
            polygons and also creates a new table called
            'points_aggregated_to_polygons' in the CARTO account.

            .. code:: python

                points_aggregated_to_polygons = cc.query(
                    '''
                      SELECT polygons.*, sum(points.values)
                      FROM polygons JOIN points
                      ON ST_Intersects(points.the_geom, polygons.the_geom)
                      GROUP BY polygons.the_geom, polygons.cartodb_id
                    ''',
                    table_name='points_aggregated_to_polygons',
                    decode_geom=True
                )

            Drops `my_table`

            .. code:: python

                cc.query(
                    '''
                      DROP TABLE my_table
                    '''
                )

            Updates the column `my_column` in the table `my_table`

            .. code:: python

                cc.query(
                    '''
                      UPDATE my_table SET my_column = 1
                    '''
                )

        """
        dataframe = None

        is_select_query = is_select or (is_select is None and query.strip().lower().startswith('select'))
        if is_select_query:
            if table_name:
                dataset = Dataset.from_query(query=query, context=self)
                dataset.upload(table_name=table_name)
                dataframe = dataset.download(decode_geom=decode_geom)
            else:
                dataframe = self.fetch(query, decode_geom=decode_geom)
        else:
            self.execute(query)

        return dataframe

    @utils.temp_ignore_warnings
    def map(self, layers=None, interactive=True,
            zoom=None, lat=None, lng=None, size=(800, 400),
            ax=None):
        """Produce a CARTO map visualizing data layers.

        Examples:
            Create a map with two data :py:class:`Layer
            <cartoframes.layer.Layer>`\\s, and one :py:class:`BaseMap
            <cartoframes.layer.BaseMap>` layer::

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
            layers (list, optional): List of zero or more of the following:

                - :py:class:`Layer <cartoframes.layer.Layer>`: cartoframes
                  :py:class:`Layer <cartoframes.layer.Layer>` object for
                  visualizing data from a CARTO table. See :py:class:`Layer
                  <cartoframes.layer.Layer>` for all styling options.
                - :py:class:`BaseMap <cartoframes.layer.BaseMap>`: Basemap for
                  contextualizng data layers. See :py:class:`BaseMap
                  <cartoframes.layer.BaseMap>` for all styling options.
                - :py:class:`QueryLayer <cartoframes.layer.QueryLayer>`: Layer
                  from an arbitrary query. See :py:class:`QueryLayer
                  <cartoframes.layer.QueryLayer>` for all styling options.

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
            # move baselayer to first position
            layers.insert(0, layers.pop(base_layers[0]))

            # add labels layer if requested
            if layers[0].is_basic() and layers[0].labels == 'front':
                layers.append(BaseMap(layers[0].source,
                                      labels='front',
                                      only_labels=True))
                layers[0].labels = None
        elif not base_layers:
            # default basemap is dark with labels in back
            # labels will be changed if all geoms are non-point
            layers.insert(0, BaseMap())
            geoms = set()

        # Setup layers
        for idx, layer in enumerate(layers):
            if not layer.is_basemap:
                # get schema of style columns
                if layer.style_cols:
                    resp = self.sql_client.send(
                        utils.minify_sql((
                            'SELECT {cols}',
                            'FROM ({query}) AS _wrap',
                            'LIMIT 0',
                        )).format(cols=','.join(layer.style_cols),
                                  comma=',' if layer.style_cols else '',
                                  query=layer.orig_query),
                        **DEFAULT_SQL_ARGS)
                    self._debug_print(layer_fields=resp)
                    for stylecol, coltype in utils.dict_items(resp['fields']):
                        layer.style_cols[stylecol] = coltype['type']
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
        api_url = utils.join_url(self.creds.base_url(), 'api/v1/map')

        static_url = ('{url}.png?{params}').format(
            url=utils.join_url(api_url, 'static/named',
                               map_name, size[0], size[1]),
            params=urlencode(params))

        html = '<img src="{url}" />'.format(url=static_url)
        self._debug_print(static_url=static_url)

        # TODO: write this as a private method
        if interactive:
            netloc = urlparse(self.creds.base_url()).netloc
            domain = 'carto.com' if netloc.endswith('.carto.com') else netloc

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
                        k: utils.safe_quotes(v, escape_single_quotes=True)
                        for k, v in utils.dict_items(options)
                    },
                },
            }

            map_options = {
                'filter': ['mapnik', 'torque', ],
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

            content = self._get_iframe_srcdoc(
                config=config,
                bounds=bounds,
                options=options,
                map_options=map_options,
                top_layer_url=top_basemap_layer_url(layers)
            )

            img_html = html
            html = (
                '<iframe srcdoc="{content}" width="{width}" height="{height}">'
                '  Preview image: {img_html}'
                '</iframe>'
            ).format(content=utils.safe_quotes(content),
                     width=size[0],
                     height=size[1],
                     img_html=img_html)
            return HTML(html)
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
            return Image(url=static_url,
                         embed=True,
                         format='png',
                         width=size[0],
                         height=size[1],
                         metadata=dict(origin_url=static_url))

    def _geom_type(self, source):
        """gets geometry type(s) of specified layer"""
        if isinstance(source, AbstractLayer):
            query = source.orig_query
        else:
            query = 'SELECT * FROM "{table}"'.format(table=source)
        resp = self.sql_client.send(
            utils.minify_sql((
                'SELECT',
                '    CASE WHEN ST_GeometryType(the_geom)',
                '               in (\'ST_Point\', \'ST_MultiPoint\')',
                '         THEN \'point\'',
                '         WHEN ST_GeometryType(the_geom)',
                '              in (\'ST_LineString\', \'ST_MultiLineString\')',
                '         THEN \'line\'',
                '         WHEN ST_GeometryType(the_geom)',
                '              in (\'ST_Polygon\', \'ST_MultiPolygon\')',
                '         THEN \'polygon\'',
                '         ELSE null END AS geom_type,',
                '    count(*) as cnt',
                'FROM ({query}) AS _wrap',
                'WHERE the_geom IS NOT NULL',
                'GROUP BY 1',
                'ORDER BY 2 DESC',
            )).format(query=query),
            **DEFAULT_SQL_ARGS)
        if resp['total_rows'] > 1:
            warn('There are multiple geometry types in {query}: '
                 '{geoms}. Styling by `{common_geom}`, the most common'.format(
                     query=query,
                     geoms=','.join(g['geom_type'] for g in resp['rows']),
                     common_geom=resp['rows'][0]['geom_type']))
        elif resp['total_rows'] == 0:
            raise ValueError('No geometry for layer. Check all layer tables '
                             'and queries to ensure there are geometries.')
        return resp['rows'][0]['geom_type']

    def data_boundaries(self, boundary=None, region=None, decode_geom=False,
                        timespan=None, include_nonclipped=False):
        """
        Find all boundaries available for the world or a `region`. If
        `boundary` is specified, get all available boundary polygons for the
        region specified (if any). This method is espeically useful for getting
        boundaries for a region and, with :py:meth:`CartoContext.data
        <cartoframes.context.CartoContext.data>` and
        :py:meth:`CartoContext.data_discovery
        <cartoframes.context.CartoContext.data_discovery>`, getting tables of
        geometries and the corresponding raw measures. For example, if you want
        to analyze how median income has changed in a region (see examples
        section for more).

        Examples:

            Find all boundaries available for Australia. The columns
            `geom_name` gives us the name of the boundary and `geom_id`
            is what we need for the `boundary` argument.

            .. code:: python

                import cartoframes
                cc = cartoframes.CartoContext('base url', 'api key')
                au_boundaries = cc.data_boundaries(region='Australia')
                au_boundaries[['geom_name', 'geom_id']]

            Get the boundaries for Australian Postal Areas and map them.

            .. code:: python

                from cartoframes import Layer
                au_postal_areas = cc.data_boundaries(boundary='au.geo.POA')
                cc.write(au_postal_areas, 'au_postal_areas')
                cc.map(Layer('au_postal_areas'))

            Get census tracts around Idaho Falls, Idaho, USA, and add median
            income from the US census. Without limiting the metadata, we get
            median income measures for each census in the Data Observatory.

            .. code:: python

                cc = cartoframes.CartoContext('base url', 'api key')
                # will return DataFrame with columns `the_geom` and `geom_ref`
                tracts = cc.data_boundaries(
                    boundary='us.census.tiger.census_tract',
                    region=[-112.096642,43.429932,-111.974213,43.553539])
                # write geometries to a CARTO table
                cc.write(tracts, 'idaho_falls_tracts')
                # gather metadata needed to look up median income
                median_income_meta = cc.data_discovery(
                    'idaho_falls_tracts',
                    keywords='median income',
                    boundaries='us.census.tiger.census_tract')
                # get median income data and original table as new dataframe
                idaho_falls_income = cc.data(
                    'idaho_falls_tracts',
                    median_income_meta,
                    how='geom_refs')
                # overwrite existing table with newly-enriched dataframe
                cc.write(idaho_falls_income,
                         'idaho_falls_tracts',
                         overwrite=True)

        Args:
            boundary (str, optional): Boundary identifier for the boundaries
              that are of interest. For example, US census tracts have a
              boundary ID of ``us.census.tiger.census_tract``, and Brazilian
              Municipios have an ID of ``br.geo.municipios``. Find IDs by
              running :py:meth:`CartoContext.data_boundaries
              <cartoframes.context.CartoContext.data_boundaries>`
              without any arguments, or by looking in the `Data Observatory
              catalog <http://cartodb.github.io/bigmetadata/>`__.
            region (str, optional): Region where boundary information or,
              if `boundary` is specified, boundary polygons are of interest.
              `region` can be one of the following:

                - table name (str): Name of a table in user's CARTO account
                - bounding box (list of float): List of four values (two
                  lng/lat pairs) in the following order: western longitude,
                  southern latitude, eastern longitude, and northern latitude.
                  For example, Switzerland fits in
                  ``[5.9559111595,45.8179931641,10.4920501709,47.808380127]``
            timespan (str, optional): Specific timespan to get geometries from.
              Defaults to use the most recent. See the Data Observatory catalog
              for more information.
            decode_geom (bool, optional): Whether to return the geometries as
              Shapely objects or keep them encoded as EWKB strings. Defaults
              to False.
            include_nonclipped (bool, optional): Optionally include
              non-shoreline-clipped boundaries. These boundaries are the raw
              boundaries provided by, for example, US Census Tiger.

        Returns:
            pandas.DataFrame: If `boundary` is specified, then all available
            boundaries and accompanying `geom_refs` in `region` (or the world
            if `region` is ``None`` or not specified) are returned. If
            `boundary` is not specified, then a DataFrame of all available
            boundaries in `region` (or the world if `region` is ``None``)
        """
        # TODO: create a function out of this?
        if isinstance(region, str):
            # see if it's a table
            try:
                geom_type = self._geom_type(region)
                if geom_type in ('point', 'line', ):
                    bounds = ('(SELECT ST_ConvexHull(ST_Collect(the_geom)) '
                              'FROM {table})').format(table=region)
                else:
                    bounds = ('(SELECT ST_Union(the_geom) '
                              'FROM {table})').format(table=region)
            except CartoException:
                # see if it's a Data Obs region tag
                regionsearch = '"geom_tags"::text ilike \'%{}%\''.format(
                    get_countrytag(region))
                bounds = 'ST_MakeEnvelope(-180.0, -85.0, 180.0, 85.0, 4326)'
        elif isinstance(region, collections.Iterable):
            if len(region) != 4:
                raise ValueError(
                    '`region` should be a list of the geographic bounds of a '
                    'region in the following order: western longitude, '
                    'southern latitude, eastern longitude, and northern '
                    'latitude. For example, Switerland fits in '
                    '``[5.9559111595,45.8179931641,10.4920501709,'
                    '47.808380127]``.')
            bounds = ('ST_MakeEnvelope({0}, {1}, {2}, {3}, 4326)').format(
                *region)
        elif region is None:
            bounds = 'ST_MakeEnvelope(-180.0, -85.0, 180.0, 85.0, 4326)'
        else:
            raise ValueError('`region` must be a str, a list of two lng/lat '
                             'pairs, or ``None`` (which defaults to the '
                             'world)')
        if include_nonclipped:
            clipped = None
        else:
            clipped = (r"(geom_id ~ '^us\.census\..*_clipped$' OR "
                       r"geom_id !~ '^us\.census\..*')")

        if boundary is None:
            regionsearch = locals().get('regionsearch')
            filters = ' AND '.join(r for r in [regionsearch, clipped] if r)
            query = utils.minify_sql((
                'SELECT *',
                'FROM OBS_GetAvailableGeometries(',
                '  {bounds}, null, null, null, {timespan})',
                '{filters}')).format(
                    bounds=bounds,
                    timespan=utils.pgquote(timespan),
                    filters='WHERE {}'.format(filters) if filters else '')
            return self.fetch(query, decode_geom=True)

        query = utils.minify_sql((
            'SELECT the_geom, geom_refs',
            'FROM OBS_GetBoundariesByGeometry(',
            '    {bounds},',
            '    {boundary},',
            '    {time})', )).format(
                bounds=bounds,
                boundary=utils.pgquote(boundary),
                time=utils.pgquote(timespan))
        return self.fetch(query, decode_geom=decode_geom)

    def data_discovery(self, region, keywords=None, regex=None, time=None,
                       boundaries=None, include_quantiles=False):
        """Discover Data Observatory measures. This method returns the full
        Data Observatory metadata model for each measure or measures that
        match the conditions from the inputs. The full metadata in each row
        uniquely defines a measure based on the timespan, geographic
        resolution, and normalization (if any). Read more about the metadata
        response in `Data Observatory
        <https://carto.com/docs/carto-engine/data/measures-functions/#obs_getmetaextent-geometry-metadata-json-max_timespan_rank-max_score_rank-target_geoms>`__
        documentation.

        Internally, this method finds all measures in `region` that match the
        conditions set in `keywords`, `regex`, `time`, and `boundaries` (if
        any of them are specified). Then, if `boundaries` is not specified, a
        geographical resolution for that measure will be chosen subject to the
        type of region specified:

          1. If `region` is a table name, then a geographical resolution that
             is roughly equal to `region size / number of subunits`.
          2. If `region` is a country name or bounding box, then a geographical
             resolution will be chosen roughly equal to `region size / 500`.

        Since different measures are in some geographic resolutions and not
        others, different geographical resolutions for different measures are
        oftentimes returned.

        .. tip::

            To remove the guesswork in how geographical resolutions are
            selected, specify one or more boundaries in `boundaries`. See
            the boundaries section for each region in the `Data Observatory
            catalog <http://cartodb.github.io/bigmetadata/>`__.

        The metadata returned from this method can then be used to create raw
        tables or for augmenting an existing table from these measures using
        :py:meth:`CartoContext.data <cartoframes.context.CartoContext.data>`.
        For the full Data Observatory catalog, visit
        https://cartodb.github.io/bigmetadata/. When working with the metadata
        DataFrame returned from this method, be careful to only remove rows not
        columns as `CartoContext.data <cartoframes.context.CartoContext.data>`
        generally needs the full metadata.

        .. note::
            Narrowing down a discovery query using the `keywords`, `regex`, and
            `time` filters is important for getting a manageable metadata
            set. Besides there being a large number of measures in the DO, a
            metadata response has acceptable combinations of measures with
            demonimators (normalization and density), and the same measure from
            other years.

            For example, setting the region to be United States counties with
            no filter values set will result in many thousands of measures.

        Examples:

            Get all European Union measures that mention ``freight``.

            .. code::

                meta = cc.data_discovery('European Union',
                                         keywords='freight',
                                         time='2010')
                print(meta['numer_name'].values)

        Arguments:
            region (str or list of float): Information about the region of
              interest. `region` can be one of three types:

                - region name (str): Name of region of interest. Acceptable
                  values are limited to: 'Australia', 'Brazil', 'Canada',
                  'European Union', 'France', 'Mexico', 'Spain',
                  'United Kingdom', 'United States'.
                - table name (str): Name of a table in user's CARTO account
                  with geometries. The region will be the bounding box of
                  the table.

                  .. Note:: If a table name is also a valid Data Observatory
                      region name, the Data Observatory name will be chosen
                      over the table.

                - bounding box (list of float): List of four values (two
                  lng/lat pairs) in the following order: western longitude,
                  southern latitude, eastern longitude, and northern latitude.
                  For example, Switzerland fits in
                  ``[5.9559111595,45.8179931641,10.4920501709,47.808380127]``

                .. Note:: Geometry levels are generally chosen by subdividing
                    the region into the next smallest administrative unit. To
                    override this behavior, specify the `boundaries` flag. For
                    example, set `boundaries` to
                    ``'us.census.tiger.census_tract'`` to choose US census
                    tracts.

            keywords (str or list of str, optional): Keyword or list of
              keywords in measure description or name. Response will be matched
              on all keywords listed (boolean `or`).
            regex (str, optional): A regular expression to search the measure
              descriptions and names. Note that this relies on PostgreSQL's
              case insensitive operator ``~*``. See `PostgreSQL docs
              <https://www.postgresql.org/docs/9.5/static/functions-matching.html>`__
              for more information.
            boundaries (str or list of str, optional): Boundary or list of
              boundaries that specify the measure resolution. See the
              boundaries section for each region in the `Data Observatory
              catalog <http://cartodb.github.io/bigmetadata/>`__.
            include_quantiles (bool, optional): Include quantiles calculations
              which are a calculation of how a measure compares to all measures
              in the full dataset. Defaults to ``False``. If ``True``,
              quantiles columns will be returned for each column which has it
              pre-calculated.

        Returns:
            pandas.DataFrame: A dataframe of the complete metadata model for
            specific measures based on the search parameters.

        Raises:
            ValueError: If `region` is a :obj:`list` and does not consist of
              four elements, or if `region` is not an acceptable region
            CartoException: If `region` is not a table in user account
        """
        if isinstance(region, str):
            try:
                # see if it's a DO region, nest in {}
                countrytag = '\'{{{0}}}\''.format(
                    get_countrytag(region))
                boundary = ('SELECT ST_MakeEnvelope(-180.0, -85.0, 180.0, '
                            '85.0, 4326) AS env, 500::int AS cnt')
            except ValueError:
                # TODO: make this work for general queries
                # see if it's a table
                self.sql_client.send(
                    'EXPLAIN SELECT * FROM {}'.format(region))
                boundary = (
                    'SELECT ST_SetSRID(ST_Extent(the_geom), 4326) AS env, '
                    'count(*)::int AS cnt FROM {table_name}').format(
                        table_name=region)
        elif isinstance(region, collections.Iterable):
            if len(region) != 4:
                raise ValueError(
                    '`region` should be a list of the geographic bounds of a '
                    'region in the following order: western longitude, '
                    'southern latitude, eastern longitude, and northern '
                    'latitude. For example, Switerland fits in '
                    '``[5.9559111595,45.8179931641,10.4920501709,'
                    '47.808380127]``.'
                )
            boundary = ('SELECT ST_MakeEnvelope({0}, {1}, {2}, {3}, 4326) AS '
                        'env, 500::int AS cnt'.format(*region))

        if locals().get('countrytag') is None:
            countrytag = 'null'

        if keywords:
            if isinstance(keywords, str):
                keywords = [keywords, ]
            kwsearch = ' OR '.join(
                ('numer_description ILIKE \'%{kw}%\' OR '
                 'numer_name ILIKE \'%{kw}%\'').format(kw=kw)
                for kw in keywords)
            kwsearch = '({})'.format(kwsearch)

        if regex:
            regexsearch = ('(numer_description ~* {regex} OR numer_name '
                           '~* {regex})').format(regex=utils.pgquote(regex))

        if keywords or regex:
            subjectfilters = '{kw} {op} {regex}'.format(
                kw=kwsearch if keywords else '',
                op='OR' if (keywords and regex) else '',
                regex=regexsearch if regex else '').strip()
        else:
            subjectfilters = ''

        if isinstance(time, str) or time is None:
            time = [time, ]
        if isinstance(boundaries, str) or boundaries is None:
            boundaries = [boundaries, ]

        if all(time) and all(boundaries):
            bt_filters = 'valid_geom AND valid_timespan'
        elif all(time) or all(boundaries):
            bt_filters = 'valid_geom' if all(boundaries) else 'valid_timespan'
        else:
            bt_filters = ''

        if bt_filters and subjectfilters:
            filters = 'WHERE ({s}) AND ({bt})'.format(
                s=subjectfilters, bt=bt_filters)
        elif bt_filters or subjectfilters:
            filters = 'WHERE {f}'.format(f=subjectfilters or bt_filters)
        else:
            filters = ''

        quantiles = ('WHERE numer_aggregate <> \'quantile\''
                     if not include_quantiles else '')

        numer_query = utils.minify_sql((
            'SELECT',
            '    numer_id,',
            '    {geom_id} AS geom_id,',
            '    {timespan} AS numer_timespan,',
            '    {normalization} AS normalization',
            '  FROM',
            '    OBS_GetAvailableNumerators(',
            '        (SELECT env FROM envelope),',
            '        {countrytag},',
            '        null,',  # denom_id
            '        {geom_id},',
            '        {timespan})',
            '{filters}', )).strip()

        # query all numerators for all `time`, `boundaries`, and raw/derived
        numers = '\nUNION\n'.join(
            numer_query.format(
                timespan=utils.pgquote(t),
                geom_id=utils.pgquote(b),
                normalization=utils.pgquote(n),
                countrytag=countrytag,
                filters=filters)
            for t in time
            for b in boundaries
            for n in ('predenominated', None))

        query = utils.minify_sql((
            'WITH envelope AS (',
            '    {boundary}',
            '), numers AS (',
            '  {numers}',
            ')',
            'SELECT *',
            'FROM json_to_recordset(',
            '    (SELECT OBS_GetMeta(',
            '        envelope.env,',
            '        json_agg(numers),',
            '        10, 10, envelope.cnt',
            '    ) AS meta',
            'FROM numers, envelope',
            'GROUP BY env, cnt)) as data(',
            '    denom_aggregate text, denom_colname text,',
            '    denom_description text, denom_geomref_colname text,',
            '    denom_id text, denom_name text, denom_reltype text,',
            '    denom_t_description text, denom_tablename text,',
            '    denom_type text, geom_colname text, geom_description text,',
            '    geom_geomref_colname text, geom_id text, geom_name text,',
            '    geom_t_description text, geom_tablename text,',
            '    geom_timespan text, geom_type text, id numeric,',
            '    max_score_rank text, max_timespan_rank text,',
            '    normalization text, num_geoms numeric, numer_aggregate text,',
            '    numer_colname text, numer_description text,',
            '    numer_geomref_colname text, numer_id text,',
            '    numer_name text, numer_t_description text,',
            '    numer_tablename text, numer_timespan text,',
            '    numer_type text, score numeric, score_rank numeric,',
            '    score_rownum numeric, suggested_name text,',
            '    target_area text, target_geoms text, timespan_rank numeric,',
            '    timespan_rownum numeric)',
            '{quantiles}', )).format(
                boundary=boundary,
                numers=numers,
                quantiles=quantiles).strip()
        self._debug_print(query=query)
        return self.fetch(query, decode_geom=True)

    def data(self, table_name, metadata, persist_as=None, how='the_geom'):
        """Get an augmented CARTO dataset with `Data Observatory
        <https://carto.com/data-observatory>`__ measures. Use
        `CartoContext.data_discovery
        <#context.CartoContext.data_discovery>`__ to search for available
        measures, or see the full `Data Observatory catalog
        <https://cartodb.github.io/bigmetadata/index.html>`__. Optionally
        persist the data as a new table.

        Example:
            Get a DataFrame with Data Observatory measures based on the
            geometries in a CARTO table.

            .. code::

                cc = cartoframes.CartoContext(BASEURL, APIKEY)
                median_income = cc.data_discovery('transaction_events',
                                                  regex='.*median income.*',
                                                  time='2011 - 2015')
                df = cc.data('transaction_events',
                             median_income)

            Pass in cherry-picked measures from the Data Observatory catalog.
            The rest of the metadata will be filled in, but it's important to
            specify the geographic level as this will not show up in the column
            name.

            .. code::

                median_income = [{'numer_id': 'us.census.acs.B19013001',
                                  'geom_id': 'us.census.tiger.block_group',
                                  'numer_timespan': '2011 - 2015'}]
                df = cc.data('transaction_events', median_income)

        Args:
            table_name (str): Name of table on CARTO account that Data
                Observatory measures are to be added to.
            metadata (pandas.DataFrame): List of all measures to add to
                `table_name`. See :py:meth:`CartoContext.data_discovery
                <cartoframes.context.CartoContext.data_discovery>` outputs
                for a full list of metadata columns.
            persist_as (str, optional): Output the results of augmenting
                `table_name` to `persist_as` as a persistent table on CARTO.
                Defaults to ``None``, which will not create a table.
            how (str, optional): **Not fully implemented**. Column name for
                identifying the geometry from which to fetch the data. Defaults
                to `the_geom`, which results in measures that are spatially
                interpolated (e.g., a neighborhood boundary's population will
                be calculated from underlying census tracts). Specifying a
                column that has the geometry identifier (for example, GEOID for
                US Census boundaries), results in measures directly from the
                Census for that GEOID but normalized how it is specified in the
                metadata.

        Returns:
            pandas.DataFrame: A DataFrame representation of `table_name` which
            has new columns for each measure in `metadata`.

        Raises:
            NameError: If the columns in `table_name` are in the
              ``suggested_name`` column of `metadata`.
            ValueError: If metadata object is invalid or empty, or if the
              number of requested measures exceeds 50.
            CartoException: If user account consumes all of Data Observatory
              quota
        """
        # if how != 'the_geom':
        #   raise NotImplementedError('Data gathering currently only works if '
        #                             'a geometry is present')
        if isinstance(metadata, pd.DataFrame):
            _meta = metadata.copy().reset_index()
        elif isinstance(metadata, collections.Iterable):
            query = utils.minify_sql((
                'WITH envelope AS (',
                '  SELECT',
                '    ST_SetSRID(ST_Extent(the_geom)::geometry, 4326) AS env,',
                '    count(*)::int AS cnt',
                '  FROM {table_name}',
                ')',
                'SELECT *',
                '  FROM json_to_recordset(',
                '      (SELECT OBS_GetMeta(',
                '          envelope.env,',
                '          (\'{meta}\')::json,',
                '          10, 1, envelope.cnt',
                '      ) AS meta',
                '  FROM envelope',
                '  GROUP BY env, cnt)) as data(',
                '      denom_aggregate text, denom_colname text,',
                '      denom_description text, denom_geomref_colname text,',
                '      denom_id text, denom_name text, denom_reltype text,',
                '      denom_t_description text, denom_tablename text,',
                '      denom_type text, geom_colname text,',
                '      geom_description text,geom_geomref_colname text,',
                '      geom_id text, geom_name text, geom_t_description text,',
                '      geom_tablename text, geom_timespan text,',
                '      geom_type text, id numeric, max_score_rank text,',
                '      max_timespan_rank text, normalization text, num_geoms',
                '      numeric,numer_aggregate text, numer_colname text,',
                '      numer_description text, numer_geomref_colname text,',
                '      numer_id text, numer_name text, numer_t_description',
                '      text, numer_tablename text, numer_timespan text,',
                '      numer_type text, score numeric, score_rank numeric,',
                '      score_rownum numeric, suggested_name text,',
                '      target_area text, target_geoms text, timespan_rank',
                '      numeric, timespan_rownum numeric)',
            )).format(table_name=table_name,
                      meta=json.dumps(metadata).replace('\'', '\'\''))
            _meta = self.fetch(query)

        if _meta.shape[0] == 0:
            raise ValueError('There are no valid metadata entries. Check '
                             'inputs.')
        elif _meta.shape[0] > 50:
            raise ValueError('The number of metadata entries exceeds 50. Tip: '
                             'If `metadata` is a pandas.DataFrame, iterate '
                             'over this object using `metadata.groupby`. If '
                             'it is a list, iterate over chunks of it. Then '
                             'combine resulting DataFrames using '
                             '`pandas.concat`')

        # get column names except the_geom_webmercator
        dataset = Dataset.from_table(table_name, context=self)
        table_columns = dataset.get_table_column_names(exclude=['the_geom_webmercator'])

        names = {}
        for suggested in _meta['suggested_name']:
            if suggested in table_columns:
                names[suggested] = utils.unique_colname(suggested, table_columns)
                warn(
                    '{s0} was augmented as {s1} because of name '
                    'collision'.format(s0=suggested, s1=names[suggested])
                )
            else:
                names[suggested] = suggested

        # drop description columns to lighten the query
        meta_columns = _meta.columns.values
        drop_columns = []
        for meta_column in meta_columns:
            if meta_column.endswith('_description'):
                drop_columns.append(meta_column)

        if len(drop_columns) > 0:
            _meta.drop(drop_columns, axis=1, inplace=True)

        cols = ', '.join(
            '(data->{n}->>\'value\')::{pgtype} AS {col}'.format(
                n=row[0],
                pgtype=row[1]['numer_type'],
                col=names[row[1]['suggested_name']])
            for row in _meta.iterrows())
        query = utils.minify_sql((
            'SELECT {table_cols}, {cols}',
            '  FROM OBS_GetData(',
            '       (SELECT array_agg({how})',
            '        FROM "{tablename}"),',
            '       (SELECT \'{meta}\'::json)) as m,',
            '       {tablename} as t',
            ' WHERE t."{rowid}" = m.id',)).format(
                how=('(the_geom, cartodb_id)::geomval'
                     if how == 'the_geom' else how),
                tablename=table_name,
                rowid='cartodb_id' if how == 'the_geom' else how,
                cols=cols,
                table_cols=','.join('t.{}'.format(c) for c in table_columns),
                meta=_meta.to_json(orient='records').replace('\'', '\'\''))

        return self.query(query, table_name=persist_as, decode_geom=False, is_select=True)

    def _auth_send(self, relative_path, http_method, **kwargs):
        self._debug_print(relative_path=relative_path,
                          http_method=http_method,
                          kwargs=kwargs)
        res = self.auth_client.send(relative_path, http_method, **kwargs)
        if isinstance(res.content, str):
            return json.loads(res.content)
        try:
            return json.loads(res.content.decode('utf-8'))
        except json.JSONDecodeError as err:
            raise CartoException(err)

    def _check_query(self, query, style_cols=None):
        """Checks if query from Layer or QueryLayer is valid"""
        try:
            self.sql_client.send(
                utils.minify_sql((
                    'EXPLAIN',
                    'SELECT',
                    '  {style_cols}{comma}',
                    '  the_geom, the_geom_webmercator',
                    'FROM ({query}) _wrap;',
                )).format(query=query,
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
            if 'errors' in resp:
                resp = self._auth_send(
                    'api/v1/map/named/{}'.format(map_name),
                    'PUT',
                    headers={'Content-Type': 'application/json'},
                    data=get_map_template(layers, has_zoom=has_zoom))
                if 'errors' in resp:
                    raise CartoException(resp)

            self._map_templates[map_name] = True
        return map_name

    def _get_iframe_srcdoc(self, config, bounds, options, map_options,
                           top_layer_url=None):
        if not hasattr(self, '_srcdoc') or self._srcdoc is None:
            html_template = os.path.join(
                os.path.dirname(__file__),
                'assets',
                'cartoframes.html')
            with open(html_template, 'r') as html_file:
                self._srcdoc = html_file.read()

        return (self._srcdoc
                .replace('@@CONFIG@@', json.dumps(config))
                .replace('@@BOUNDS@@', json.dumps(bounds))
                .replace('@@OPTIONS@@', json.dumps(map_options))
                .replace('@@LABELS@@', top_layer_url or '')
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
            utils.minify_sql((
                'SELECT',
                '    ST_XMIN(ext) AS west,',
                '    ST_YMIN(ext) AS south,',
                '    ST_XMAX(ext) AS east,',
                '    ST_YMAX(ext) AS north',
                'FROM (',
                '    SELECT ST_Extent(the_geom) AS ext',
                '    FROM ({union_query}) AS _wrap1',
                ') AS _wrap2',
            )).format(union_query=union_query),
            do_post=False)

        return extent['rows'][0]

    def _debug_print(self, **kwargs):
        if self._verbose <= 0:
            return

        for key, value in utils.dict_items(kwargs):
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
