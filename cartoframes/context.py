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
import re
import sys
import time
import collections

import requests
import IPython
import pandas as pd

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient

from cartoframes.utils import dict_items
from cartoframes.layer import BaseMap
from cartoframes.maps import non_basemap_layers, get_map_name, get_map_template

if sys.version_info >= (3, 0):
    from urllib.parse import urlparse, urlencode
else:
    from urlparse import urlparse
    from urllib import urlencode

class CartoContext:
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
            documentation <http://docs.python-requests.org/en/master/user/advanced/>`__
            for more information:
        verbose (bool, optional): Output underlying process states (True), or
            suppress (False, default)

    Returns:
        :obj:`CartoContext`: A CartoContext object that is authenticated against
        the user's CARTO account.
    """
    def __init__(self, base_url=None, api_key=None, session=None, verbose=0):

        # use stored api key (if present)
        if (api_key is None) or (base_url is None):
            from cartoframes import keys 
            credentials = keys.credentials()
            api_key = credentials['api_key'] if api_key is None else api_key
            base_url = credentials['base_url'] if base_url is None else base_url
            if (api_key == '') and (base_url == ''):
                raise ValueError('No credentials are stored on this installation'
                                 ' and none were provided. Use `cartoframes.keys.set_credentials`'
                                 ' to store your access url and api key for this installation')
            if api_key == '':
                raise ValueError('API Key was not provided and no key is '
                                 'stored. Use `cartoframes.keys.set_key` '
                                 'to set a default key for this installation')
            if base_url == '':
                raise ValueError('Base URL was not provided and no url is stored.'
                                 'Use `cartoframes.keys.set_url` to set a default'
                                 ' bsae url for this installation')

        # Make sure there is a trailing / for urljoin
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url
        self.api_key = api_key

        url_info = urlparse(base_url)
        # On-Prem:
        #   /user/<username>
        username = re.search('^/user/(.*)/$', url_info.path)
        if username is None:
            # Cloud personal account
            # <username>.carto.com
            username = re.search(r'^(.*?)\..*', url_info.netloc)
        self.username = username.group(1)

        self.auth_client = APIKeyAuthClient(base_url=base_url,
                                            api_key=api_key,
                                            session=session)
        self.sql_client = SQLClient(self.auth_client)

        res = self.sql_client.send('SHOW search_path')

        paths = [p.strip() for p in res['rows'][0]['search_path'].split(',')]
        # is an org user if first item is not `public`

        self.is_org = (paths[0] != 'public')

        self._map_templates = {}
        self._srcdoc = None

        self._verbose = verbose


    def read(self, table_name, limit=None, index='cartodb_id'):
        """Read tables from CARTO into pandas DataFrames.

        Example:
        ::

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
            if (limit >= 0) and isinstance(limit, int):
                query += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")

        return self.query(query)


    def write(self, df, table_name, temp_dir='/tmp', overwrite=False,
              lnglat=None):
        """Write a DataFrame to a CARTO table.

        Example:
        ::

            cc.write(df, 'brooklyn_poverty', overwrite=True)

        Args:
            df (pandas.DataFrame): DataFrame to write to ``table_name`` in user
                CARTO account
            table_name (str): Table to write ``df`` to in CARTO.
            temp_dir (str, optional): Directory for temporary storage of data
                that is sent to CARTO. Defaults to ``/tmp`` (Unix-like systems).
            overwrite (bool, optional): Behavior for overwriting ``table_name``
                if it exits on CARTO. Defaults to ``False``.
            lnglat (tuple, optional): lng/lat pair that can be used for creating
                a geometry on CARTO. Defaults to ``None``. In some cases,
                geometry will be created without specifying this. See CARTO's
                `Import API <https://carto.com/docs/carto-engine/import-api/standard-tables>`__
                for more information.

        Returns:
            None
        """
        table_exists = True
        if not overwrite:
            try:
                self.query('SELECT * FROM {table_name} limit 0'.format(table_name=table_name))
            except Exception as err:
                self._debug_print(err=err)
                # If table doesn't exist, we get an error from the SQL API
                table_exists = False

            if table_exists:
                raise AssertionError(
                    ('Table {table_name} already exists. '
                     'Run with overwrite=True if you wish to replace the '
                     'table').format(table_name=table_name))

        tempfile = '{temp_dir}/{table_name}.csv'.format(temp_dir=temp_dir,
                                                        table_name=table_name)
        self._debug_print(tempfile=tempfile)

        def remove_tempfile():
            """removes temporary file"""
            os.remove(tempfile)

        df.to_csv(tempfile)

        with open(tempfile, 'rb') as f:
            res = self._auth_send('api/v1/imports', 'POST',
                                  files={'file': f},
                                  stream=True)
            self._debug_print(res=res)

            if not res['success']:
                remove_tempfile()
                raise Exception('Failed to send')
            import_id = res['item_queue_id']

            while True:
                res = self._auth_send('api/v1/imports/{}'.format(import_id),
                                      'GET')
                if res['state'] == 'failure':
                    remove_tempfile()
                    raise Exception('Error code: {}'.format(res['error_code']))
                if res['state'] == 'complete':
                    break
                # Wait half a second before doing another request
                time.sleep(0.5)

            remove_tempfile()

        if lnglat:
            self.query('''
                UPDATE "{table_name}"
                SET the_geom = CDB_LatLng({lat}, {lng})
            '''.format(table_name=table_name,
                       lng=lnglat[0],
                       lat=lnglat[1]))


    def sync(self, dataframe, table_name):
        """Depending on the size of the DataFrame or CARTO table, perform
        granular operations on a DataFrame to only update the changed cells
        instead of a bulk upload. If on the large side, perform granular
        operations, if on the smaller side use Import API.

        Note:
            Not yet implemented.
        """
        pass


    def query(self, query, table_name=None):
        """Pull the result from an arbitrary SQL query from a CARTO account
        into a pandas DataFrame.

        Args:
            query (str): Query to run against CARTO user database.
            table_name (str, optional): If set, this will create a new
                table in the user's CARTO account that is the result of the
                query. Defaults to None (no table created).
        Returns:
            pandas.DataFrame: DataFrame representation of query supplied.
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
                       org=(self.username if self.is_org else 'public'))
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

        pg2dtypes = {
            'date': 'datetime64',
            'number': 'float64',
            'string': 'object',
            'boolean': 'bool',
            'geometry': 'object',
        }

        fields = select_res['fields']
        schema = {
            field: pg2dtypes.get(fields[field]['type'], 'object')
                   if field != 'cartodb_id' else 'int64'
            for field in fields
        }
        self._debug_print(fields=fields, schema=schema)

        df = pd.DataFrame(
            data=select_res['rows'],
            columns=[k for k in fields]).astype(schema)
        if 'cartodb_id' in fields:
            df.set_index('cartodb_id', inplace=True)
        return df


    def map(self, layers=None, interactive=True,
            zoom=None, lat=None, lng=None, size=(800, 400)):
        """Produce a CARTO map visualizing data layers.

        Example:
            Create a map with two data layers, and one BaseMap layer.
            ::

                import cartoframes
                from cartoframes import Layer, BaseMap
                cc = cartoframes.CartoContext(BASEURL, APIKEY)
                cc.map(layers=[BaseMap(),
                               Layer('acadia_biodiversity',
                                     color={'column': 'simpson_index',
                                            'scheme': 'TealRose'}),
                               Layer('peregrine_falcon_nest_sites',
                                     size='num_eggs',
                                     color={'column': 'bird_id',
                                            'scheme': 'Vivid')],
                       interactive=True)
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
            size (tuple, optional): List of pixel dimensions for the map. Format
                is ``(width, height)``. Defaults to ``(800, 400)``.

        Returns:
            IPython.display.HTML: Interactive maps are rendered in an ``iframe``,
            while static maps are rendered in ``img`` tags.
        """
        if layers is None:
            layers = []
        elif not isinstance(layers, collections.Iterable):
            layers = [layers]
        else:
            layers = list(layers)

        if len(layers) > 8:
            raise ValueError('map can have at most 8 layers')

        if any([zoom, lat, lng]) != all([zoom, lat, lng]):
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
            raise ValueError('map can at most take 1 Layer with time column/field')
        if time_layer:
            if not interactive:
                raise ValueError('map cannot display a static image with a time_column')
            layers.append(layers.pop(time_layers[0]))

        # If basemap labels are on front, add labels layer
        basemap = layers[0]
        if basemap.is_basic() and basemap.labels == 'front':
            layers.append(BaseMap(basemap.source,
                                  labels=basemap.labels,
                                  only_labels=True))

        # Setup layers
        for idx, layer in enumerate(layers):
            layer._setup(self, layers, idx)

        nb_layers = non_basemap_layers(layers)
        options = {'basemap_url': basemap.url}

        # Reverse layers to put torque's Map first
        for idx, layer in enumerate(nb_layers):
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
        api_url = '{base_url}api/v1/map'.format(base_url=self.base_url)

        static_url = ('{api_url}/static/named/{map_name}'
                      '/{width}/{height}.png?{params}').format(
                          api_url=api_url,
                          map_name=map_name,
                          width=size[0],
                          height=size[1],
                          params=urlencode(params))

        html = '<img src="{url}" />'.format(url=static_url)

        if interactive:
            netloc = urlparse(self.base_url).netloc
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
                'user_name': self.username,
                'maps_api_template': self.base_url[:-1],
                'sql_api_template': self.base_url[:-1],
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
                        'user_name': self.username,
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
            Add new measures to a CARTO table and pass it to a pandas DataFrame.
            Using the "Median Household Income in the past 12 months" measure
            from the `Data Observatory Catalog
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
                - `normalization` (str, optional): The desired normalization. One
                  of 'area', 'prenormalized', or 'denominated'. 'Area' will
                  normalize the measure per square kilometer, 'prenormalized'
                  will return the original value, and 'denominated' will
                  normalize by a denominator.
                - `denom_id` (str, optional): Measure ID from DO catalog
                - `numer_timespan` (str, optional): The desired timespan for the
                  measurement. Defaults to most recent timespan available if
                  left unspecified.
                - `geom_timespan` (str, optional): The desired timespan for the
                  geometry. Defaults to timespan matching `numer_timespan` if
                  left unspecified.
                - `target_area` (str, optional): Instead of aiming to have
                  `target_geoms` in the area of the geometry passed as extent,
                  fill this area. Unit is square degrees WGS84. Set this to
                  `0` if you want to use the smallest source geometry for this
                  element of metadata, for example if you're passing in points.
                - `target_geoms` (str, optional): Override global `target_geoms`
                  for this element of metadata
                - `max_timespan_rank` (str, optional): Override global
                  `max_timespan_rank` for this element of metadata
                - `max_score_rank` (str, optional): Override global
                  `max_score_rank` for this element of metadata

        Returns:
            pandas.DataFrame: A DataFrame representation of `table_name` which
            has new columns for each measure in `metadata`.
        """

        # augment with data observatory metadata
        augment_query = '''
            select obs_augment_table('{username}.{tablename}',
                                     '{cols_meta}');
        '''.format(username=self.username,
                   tablename=table_name,
                   cols_meta=json.dumps(metadata))
        resp = self.sql_client.send(augment_query)

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


    def _send_map_template(self, layers, has_zoom):
        map_name = get_map_name(layers, has_zoom=has_zoom)
        if map_name not in self._map_templates:
            try:
                self._auth_send('api/v1/map/named', 'POST',
                                headers={'Content-Type': 'application/json'},
                                data=get_map_template(layers, has_zoom=has_zoom))
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
                .replace('@@CONFIG@@', str(config))
                .replace('@@BOUNDS@@', str(bounds))
                .replace('@@OPTIONS@@', str(map_options))
                .replace('@@ZOOM@@', str(options.get('zoom', 3)))
                .replace('@@LAT@@', str(options.get('lat', 0)))
                .replace('@@LNG@@', str(options.get('lng', 0))))


    def _get_bounds(self, layers):
        """Return the bounds of all data layers involved in a cartoframes
        map.

        Args:
            layers (list): List of cartoframes layers. See `cartoframes.layers`
                for all types.

        Returns:
            dict: Dictionary of northern, southern, eastern, and western bounds
                of the superset of data layers. Keys are `north`, `south`,
                `east`, and `west`. Units are in WGS84.
        """
        extent_query = ('SELECT ST_EXTENT(the_geom) AS the_geom '
                        'FROM ({query}) as t{idx}\n')
        union_query = 'UNION ALL\n'.join(
            [extent_query.format(query=layer.query, idx=idx)
             for idx, layer in enumerate(layers)
             if not layer.is_basemap])

        extent = self.query('''
               SELECT
                 ST_XMIN(ext) AS west,
                 ST_YMIN(ext) AS south,
                 ST_XMAX(ext) AS east,
                 ST_YMAX(ext) AS north
               FROM (
                   SELECT st_extent(the_geom) AS ext
                   FROM ({union_query}) AS wrap1
               ) AS wrap2'''.format(union_query=union_query))

        west, south, east, north = extent.values[0]

        return {
            'west' : west,
            'south': south,
            'east' : east,
            'north': north,
        }


    def _debug_print(self, **kwargs):
        if self._verbose <= 0:
            return

        for key, value in dict_items(kwargs):
            if isinstance(value, requests.Response):
                str_value = "status_code: {status_code}, content: {content}".format(
                    status_code=value.status_code, content=value.content)
            else:
                str_value = str(value)
            if self._verbose < 2 and len(str_value) > 300:
                str_value = '{}\n\n...\n\n{}'.format(str_value[:250], str_value[-50:])
            print('{key}: {value}'.format(key=key,
                                          value=str_value))
