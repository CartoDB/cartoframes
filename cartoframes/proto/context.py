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

if sys.version_info >= (3,0):
    from urllib.parse import urlparse, urlencode
else:
    from urlparse import urlparse
    from urllib import urlencode

class CartoContext:
    def __init__(self, base_url, api_key, *, verbose=0):
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
                                            api_key=api_key)
        self.sql_client = SQLClient(self.auth_client)

        res = self.sql_client.send('SHOW search_path')
        paths = res['rows'][0]['search_path'].split(',')
        self.is_org = (paths[0] == 'public')

        self._map_templates = {}

        self._verbose = verbose


    def read(self, table_name, *, limit=None, index='cartodb_id'):
        q = 'SELECT * FROM "{table_name}"'.format(table_name=table_name)
        if limit:
            if (limit >= 0) and isinstance(limit, int):
                q += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")

        return self.query(q)


    def write(self, df, table_name, *, temp_dir='/tmp', overwrite=False, lnglat=None):
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


    def query(self, q, *, table_name=None):
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
            self._debug_print(create_table_res=res)

            new_table_name = create_table_res['rows'][0]['cdb_cartodbfytable']
            self._debug_print(new_table_name=new_table_name)

            select_res = carto_sql_client.send(
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
            for field in fields
        }
        self._debug_print(fields=fields, schema=schema)

        df = pd.DataFrame(
            data=select_res['rows'],
            columns=[k for k in fields]).astype(schema)
        if 'cartodb_id' in fields:
            df.set_index('cartodb_id', inplace=True)
        return df


    def map(self, *, layers=None, interactive=True,
            zoom=None, lat=None, lng=None,
            size=[800,400]):

        if layers is None:
            layers = []
        elif not isinstance(layers, collections.Iterable):
            layers = [layers]
        else:
            layers = list(layers)

        if len(layers) > 4:
            raise ValueError('map can have at most 4 layers')

        if any([zoom, lat, lng]) != all([zoom, lat, lng]):
            raise ValueError('zoom, lat, and lng must all or none be provided')

        # Call setup if needed
        basemap_idx = -1
        for idx, layer in enumerate(layers):
            if layer.is_basemap:
                if basemap_idx >= 0:
                    raise ValueError('map can at most take 1 BaseMap layer')
                basemap_idx = idx

        # Move or create BaseMap and move as first layer
        if basemap_idx < 0:
            layers.insert(0, BaseMap())
        elif basemap_idx >= 1:
            layers.insert(0, layers.pop(basemap_idx))

        # Check for a time layer, if it exists move it to the front
        time_idx = -1
        for idx, layer in enumerate(layers):
            layer._setup(self, layers)
            if not layer.is_basemap and layer.time:
                if time_idx >= 0:
                    raise ValueError('map can at most take 1 Layer with time column/field')
                time_idx = idx

        if time_idx >= 0:
            layers.append(layers.pop(time_idx))

        # If basemap labels are on front, add labels layer
        basemap = layers[0]
        if basemap.is_basic() and basemap.labels == 'front':
            layers.append(BaseMap(basemap.source,
                                  labels=basemap.labels,
                                  only_labels=True))

        has_zoom = zoom is not None

        nb_layers = non_basemap_layers(layers)
        options = {}

        for idx, layer in enumerate(nb_layers):
            options['cartocss_' + str(idx)] = layer.description
            options['query_' + str(idx)]    = layer.query

        if has_zoom:
            options['zoom'] = zoom
            options['lat']  = lat
            options['lng']  = lng
        else:
            options.update(self.get_bounds(nb_layers))

        map_name = self._send_map_template(layers, has_zoom=has_zoom)
        api_url = '{base_url}api/v1/map'.format(base_url=self.base_url)

        if interactive:
            map_url = '{api_url}/named/{map_name}'.format(api_url=api_url,
                                                          map_name=map_name)
        else:
            map_url = '{api_url}/static/named/{map_name}'.format(api_url=api_url,
                                                                 map_name=map_name)
        map_url += '?' + urlencode({'config': options})

        html = '<img src="{url}" />'.format(url=map_url)

        if interactive:
            html = (
                '<iframe src="{url}" width={width} height={height}>'
                '  Preview image: {img}'
                '</iframe>'
            ).format(url=map_url,
                     width=size[0],
                     height=size[1],
                     img=html)

        return IPython.display.HTML(html)


    def data_boundaries(self, *, df=None, table_name=None):
        pass


    def data_discovery(self, *, keywords=None, regex=None, time=None, boundary=None):
        pass


    def data_augment(self, table_name, numer, *, denom=None):
        pass


    def _auth_send(self, relative_path, http_method, **kwargs):
        res = self.auth_client.send(relative_path, http_method, **kwargs)
        return json.loads(res.content)


    def _send_map_template(self, layers, *, has_zoom):
        map_name = get_map_name(layers, has_zoom=has_zoom)
        print(self._map_templates)
        if map_name not in self._map_templates:
            try:
                self._auth_send('api/v1/map/named', 'POST',
                                headers={'Content-Type': 'application/json'},
                                data=get_map_template(layers, has_zoom=has_zoom))
            except:
                pass

            self._map_templates[map_name] = True
        return map_name


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