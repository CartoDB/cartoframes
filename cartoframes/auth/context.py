"""
This class is the workhorse of CARTOframes by providing all functionality related to
data access to CARTO, map creation, and Data Observatory functionality.
"""
from __future__ import absolute_import

import os
import json
import requests

from tqdm import tqdm
from appdirs import user_cache_dir

from carto.auth import APIKeyAuthClient, AuthAPIClient
from carto.sql import SQLClient, BatchSQLClient, CopySQLClient
from carto.exceptions import CartoException
from carto.datasets import DatasetManager
from pyrestcli.exceptions import NotFoundException

from .credentials import Credentials
from .. import utils
from ..__version__ import __version__
from ..data import Dataset

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


class Context(object):
    """Context class for authentication with CARTO and high-level
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
         :py:class:`Context <cartoframes.auth.Context>`. This method is easier.::

            con = Context(
                base_url='https://eschbacher.carto.com',
                api_key='abcdefg')

      2. By passing a :py:class:`Credentials
         <cartoframes.auth.Credentials>` instance in
         :py:class:`Context <cartoframes.auth.Context>`'s
         :py:attr:`creds <cartoframes.auth.Credentials.creds>`
         keyword argument. This method is more flexible.::

            from cartoframes.auth import Credentials
            creds = Credentials(username='eschbacher', api_key='abcdefg')
            con = Context(creds=creds)

    Attributes:
        creds (:py:class:`Credentials <cartoframes.auth.Credentials>`):
          :py:class:`Credentials <cartoframes.auth.Credentials>`
          instance

    Args:
        base_url (str): Base URL of CARTO user account. Cloud-based accounts
            should use the form ``https://{username}.carto.com`` (e.g.,
            https://eschbacher.carto.com for user ``eschbacher``) whether on
            a personal or multi-user account. On-premises installation users
            should ask their admin.
        api_key (str): CARTO API key.
        creds (:py:class:`Credentials <cartoframes.auth.Credentials>`):
          A :py:class:`Credentials <cartoframes.auth.Credentials>`
          instance can be used in place of a `base_url`/`api_key` combination.
        session (requests.Session, optional): requests session. See `requests
            documentation
            <http://docs.python-requests.org/en/master/user/advanced/>`__
            for more information.
        verbose (bool, optional): Output underlying process states (True), or
            suppress (False, default)

    Returns:
        :py:class:`Context <cartoframes.auth.Context>`: A
        Context object that is authenticated against the user's CARTO
        account.

    Example:

        Create a :py:class:`Context <cartoframes.auth.Context>` object for a cloud-based CARTO
        account.

        .. code::

            from cartoframes.auth import Context
            # if on prem, format is '{host}/user/{username}'
            BASEURL = 'https://{}.carto.com/'.format('your carto username')
            APIKEY = 'your carto api key'
            con = Context(BASEURL, APIKEY)

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

            con = cartoframes.auth.Context(
                base_url='{host}/user/{user}'.format(
                    host=onprem_host,
                    user='your carto username'),
                api_key='your carto api key',
                session=session
            )

    """

    def __init__(self, base_url=None, api_key='default_public', creds=None, session=None,
                 verbose=0):

        if creds:
            self.creds = Credentials.from_credentials(creds)
        else:
            self.creds = Credentials(api_key=api_key, base_url=base_url, session=session)

        self.auth_client = APIKeyAuthClient(
            base_url=self.creds.base_url,
            api_key=self.creds.api_key,
            session=session,
            client_id='cartoframes_{}'.format(__version__),
            user_agent='cartoframes_{}'.format(__version__)
        )
        self.auth_api_client = AuthAPIClient(
            base_url=self.creds.base_url,
            api_key=self.creds.api_key,
            session=session
        )
        self.sql_client = SQLClient(self.auth_client)
        self.copy_client = CopySQLClient(self.auth_client)
        self.batch_sql_client = BatchSQLClient(self.auth_client)
        self.creds.username = self.auth_client.username
        self._is_authenticated()
        self.is_org = self._is_org_user()

        self._map_templates = {}
        self._srcdoc = None
        self._verbose = verbose

    def _is_authenticated(self):
        """Checks if credentials allow for authenticated carto access"""
        if not self.auth_api_client.is_valid_api_key():
            raise CartoException('Cannot authenticate user `{}`. Check credentials.'.format(self.creds.username))

    def _is_org_user(self):
        """Report whether user is in a multiuser CARTO organization or not"""
        res = self.sql_client.send("select unnest(current_schemas('f'))",
                                   **DEFAULT_SQL_ARGS)
        # is an org user if first item is not `public`
        return res['rows'][0]['unnest'] != 'public'

    def get_default_schema(self):
        return 'public' if not self.is_org else self.creds.username

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
                con = cartoframes.auth.Context(BASEURL, APIKEY)
                df = con.read('acadia_biodiversity')
        """
        # choose schema (default user - org or standalone - or shared)
        schema = 'public' if not self.is_org else (shared_user or self.creds.username)

        dataset = Dataset(table_name, schema=schema, credentials=self)
        return dataset.download(limit, decode_geom, retry_times)

    @utils.temp_ignore_warnings
    def tables(self):
        """List all tables in user's CARTO account

        Returns:
            :obj:`list` of :py:class:`Dataset <cartoframes.data.Dataset>`

        """
        table_names = DatasetManager(self.auth_client).filter(
            show_table_size_and_row_count='false',
            show_table='false',
            show_stats='false',
            show_likes='false',
            show_liked='false',
            show_permission='false',
            show_uses_builder_features='false',
            show_synchronization='false',
            load_totals='false')
        return [Dataset(str(table_name)) for table_name in table_names]

    def write(self, df, table_name, temp_dir=CACHE_DIR, overwrite=False,
              lnglat=None, encode_geom=False, geom_col=None, **kwargs):
        """Write a DataFrame to a CARTO table.

        Examples:
            Write a pandas DataFrame to CARTO.

            .. code:: python

                con.write(df, 'brooklyn_poverty', overwrite=True)

            Scrape an HTML table from Wikipedia and send to CARTO with content
            guessing to create a geometry from the country column. This uses
            a CARTO Import API param `content_guessing` parameter.

            .. code:: python

                url = 'https://en.wikipedia.org/wiki/List_of_countries_by_life_expectancy'
                # retrieve first HTML table from that page
                df = pd.read_html(url, header=0)[0]
                # send to carto, let it guess polygons based on the 'country'
                #   column. Also set privacy to 'public'
                con.write(df, 'life_expectancy',
                         content_guessing=True,
                         privacy='public')
                con.map(layers=Layer('life_expectancy',
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
            :py:class:`Dataset <cartoframes.data.Dataset>`

        .. note::
            DataFrame indexes are changed to ordinary columns. CARTO creates
            an index called `cartodb_id` for every table that runs from 1 to
            the length of the DataFrame.
        """  # noqa
        tqdm.write('Params: encode_geom, geom_col and everything in kwargs are deprecated and not being used any more')
        dataset = Dataset(df)

        if_exists = Dataset.FAIL
        if overwrite:
            if_exists = Dataset.REPLACE

        dataset.upload(with_lnglat=lnglat, if_exists=if_exists, table_name=table_name, credentials=self)

        tqdm.write('Table successfully written to CARTO: {table_url}'.format(
            table_url=utils.join_url(self.creds.base_url,
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
        dataset = Dataset(table_name, credentials=self)
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
                    'the data size.'.format(self.creds.username)
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

    def _get_iframe_srcdoc(self, config, bounds, options, map_options,
                           top_layer_url=None):
        if not hasattr(self, '_srcdoc') or self._srcdoc is None:
            html_template = os.path.join(
                os.path.dirname(__file__),
                '..',
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
