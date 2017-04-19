import json
import os
import random
import re
import requests
import sys
import tempfile
import time
import collections
import IPython
import pandas as pd

import carto
from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient

from .utils import dict_items
from .layer import BaseMap
from .maps import non_basemap_layers, get_map_name, get_map_template

if sys.version_info >= (3, 0):
    from urllib.parse import urlparse, urlencode
else:
    from urlparse import urlparse
    from urllib import urlencode

class CartoContext:
    def __init__(self, base_url, api_key, session=None, verbose=0):
        # Make sure there is a trailing / for urljoin
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url
        self.api_key = api_key

        url_info = urlparse(base_url)
        # On-Prem:
        #   /user/<username>
        m = re.search('^/user/(.*)/$', url_info.path)
        if m is None:
            # Cloud personal account
            # <username>.carto.com
            m = re.search('^(.*?)\..*', url_info.netloc)
        self.username = m.group(1)

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
        q = 'SELECT * FROM "{table_name}"'.format(table_name=table_name)
        if limit:
            if (limit >= 0) and isinstance(limit, int):
                q += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")

        return self.query(q)


    def write(self, df, table_name, temp_dir='/tmp', overwrite=False, lnglat=None):
        table_exists = True
        if not overwrite:
            try:
                self.query('SELECT * FROM {table_name} limit 0'.format(table_name=table_name))
            except:
                # If table doesn't exist, we get an error from the SQL API
                table_exists = False

            if table_exists:
                raise AssertionError(
                    ('Table {table_name} already exists. '
                     'Run with overwrite=True if you wish to replace the table').format(table_name=table_name))

        tempfile = '{temp_dir}/{table_name}.csv'.format(temp_dir=temp_dir, table_name=table_name)
        self._debug_print(tempfile=tempfile)

        def remove_tempfile():
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
                res = self._auth_send('api/v1/imports/{}'.format(import_id), 'GET')
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


    def sync(self, df, table_name):
        pass


    def query(self, q, table_name=None):
        self._debug_print(query=q)
        if table_name:
            create_table_query = '''
                CREATE TABLE {table_name} As
                SELECT *
                  FROM ({query}) As _wrap;
                SELECT CDB_CartodbfyTable('{org}', '{table_name}');
            '''.format(table_name=table_name,
                       query=q,
                       org=(self.username if self.is_org else 'public'))
            self._debug_print(create_table_query=create_table_query)

            create_table_res = self.sql_client.send(create_table_query)
            self._debug_print(create_table_res=create_table_res)

            new_table_name = create_table_res['rows'][0]['cdb_cartodbfytable']
            self._debug_print(new_table_name=new_table_name)

            select_res = self.sql_client.send(
                'SELECT * FROM {table_name}'.format(table_name=new_table_name))
        else:
            select_res = self.sql_client.send(q)

        self._debug_print(select_res=select_res)

        pg2dtypes = {
            'date'    : 'datetime64',
            'number'  : 'float64',
            'string'  : 'object',
            'boolean' : 'bool',
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
            zoom=None, lat=None, lng=None,
            size=[800,400]):

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
        if len(layers) == 0 and zoom is None:
            [zoom, lat, lng] = [3, 38, -99]
        has_zoom = zoom is not None

        # Check basemaps, add one if none exist
        base_layers = [idx for idx, layer in enumerate(layers) if layer.is_basemap]
        if len(base_layers) > 1:
            raise ValueError('map can at most take 1 BaseMap layer')
        if len(base_layers) > 0:
            layers.insert(0, layers.pop(base_layers[0]))
        else:
            layers.insert(0, BaseMap())

        # Check for a time layer, if it exists move it to the front
        time_layers = [idx for idx, layer in enumerate(layers) if not layer.is_basemap and layer.time]
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
        for idx, layer in enumerate(nb_layers[::-1]):
            options['cartocss_' + str(idx)] = layer.cartocss
            options['sql_' + str(idx)]      = layer.query


        params = {
            'config'    : json.dumps(options),
            'anti_cache': random.random(),
        }

        if has_zoom:
            params.update({'zoom': zoom, 'lat': lat, 'lon': lng})
            options.update({'zoom': zoom, 'lat': lat, 'lng': lng})
        else:
            options.update(self.get_bounds(nb_layers))

        map_name = self._send_map_template(layers, has_zoom=has_zoom)
        api_url = '{base_url}api/v1/map'.format(base_url=self.base_url)

        static_url = ('{api_url}/static/named/{map_name}'
                      '/{width}/{height}.png?{params}').format(api_url=api_url,
                                                               map_name=map_name,
                                                               width=size[0],
                                                               height=size[1],
                                                               params=urlencode(params))

        html = '<img src="{url}" />'.format(url=static_url)

        if interactive:
            netloc = urlparse(self.base_url).netloc
            domain = 'carto.com' if netloc.endswith('.carto.com') else netloc

            def safe_quotes(s, escape_single_quotes=False):
                if isinstance(s, str):
                    s2 = s.replace('"', "&quot;")
                    if escape_single_quotes:
                        s2 = s2.replace("'","&#92;'")
                    return s2.replace('True', 'true')
                return s

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
                        for k,v in dict_items(options)
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
        pass


    def data_discovery(self, keywords=None, regex=None, time=None, boundary=None):
        pass


    def data_augment(self, table_name, numer, denom=None):
        pass


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
            except:
                pass

            self._map_templates[map_name] = True
        return map_name


    def _get_iframe_srcdoc(self, config, bounds, options, map_options):
        if not hasattr(self, '_srcdoc') or self._srcdoc is None:
            with open(os.path.join(os.path.dirname(__file__),
                                   'assets/cartoframes.html'), 'r') as f:
                self._srcdoc = f.read()

        return (self._srcdoc
                .replace('@@CONFIG@@' , str(config))
                .replace('@@BOUNDS@@' , str(bounds))
                .replace('@@OPTIONS@@', str(map_options))
                .replace('@@ZOOM@@', str(options.get('zoom', 3)))
                .replace('@@LAT@@' , str(options.get('lat' , 0)))
                .replace('@@LNG@@' , str(options.get('lng' , 0))))


    def get_bounds(self, layers):
        extent_query = 'SELECT ST_EXTENT(the_geom) AS the_geom FROM ({query}) as t{idx}\n'
        union_query  = 'UNION ALL\n'.join(extent_query.format(query=layer.query, idx=idx)
                                          for idx, layer in enumerate(layers)
                                          if not layer.is_basemap)
        df = self.query('''
               SELECT
                 ST_XMIN(ext) AS west,
                 ST_YMIN(ext) AS south,
                 ST_XMAX(ext) AS east,
                 ST_YMAX(ext) AS north
               FROM (
                   SELECT st_extent(the_geom) AS ext
                   FROM ({union_query}) AS wrap1
               ) AS wrap2'''.format(union_query=union_query))

        west, south, east, north = df.values[0]

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
            if type(value) == requests.Response:
                str_value = "status_code: {status_code}, content: {content}".format(
                    status_code=value.status_code, content=value.content)
            else:
                str_value = str(value)
            if self._verbose < 2 and len(str_value) > 300:
                str_value = '{}\n\n...\n\n{}'.format(str_value[:250], str_value[-50:])
            print('{key}: {value}'.format(key=key,
                                          value=str_value))
