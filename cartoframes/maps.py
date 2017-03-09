"""
Functions and methods for interactive and static maps
"""

import pandas as pd

def create_named_map(username, api_key, tablename):
    """Create a named map for later use
    """
    import json
    from time import time
    import requests

    map_name = '{table}_{time}'.format(table=tablename,
                                       time=str(time()).replace('.', '_'))
    print("map name: {}".format(map_name))

    defaults = {'named_map_name': map_name,
                'basemap': 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png',
                'cartocss': '#layer{ marker-width: 7; marker-fill: #00F; }',
                'tablename': tablename,
                'west': -45,
                'south': -45,
                'east': 45,
                'north': 45}

    filled_template = get_named_map_template() % defaults

    api_endpoint = ('https://{username}.carto.com/api/v1/map/named'
                    '?api_key={api_key}').format(username=username,
                                                 api_key=api_key)
    print("api_endpoint: {}".format(api_endpoint))
    resp = requests.post(api_endpoint,
                         data=filled_template,
                         headers={'content-type': 'application/json'})
    print("response: {}".format(resp))
    if resp.status_code == requests.codes.ok:
        return json.loads(resp.text)['template_id']
    else:
        resp.raise_for_status()

    return None


def get_bounds(self, debug=False):
    """Get the southwestern most point, and northeastern most point"""

    query = '''
        SELECT
          ST_XMin(ext) as west,
          ST_YMin(ext) as south,
          ST_XMax(ext) as east,
          ST_YMax(ext) as north
        FROM (SELECT ST_Extent(the_geom) as ext
              FROM {tablename}) as _wrap
    '''.format(tablename=self.get_carto_tablename())
    bounds = self.carto_sql_client.send(query)
    if debug: print(bounds['rows'][0])
    return bounds['rows'][0]


def get_static_snapshot(self, cartocss, basemap, debug=False):
    """update a named map with a new configuration"""
    import requests
    if basemap:
        new_basemap = basemap
    else:
        new_basemap = 'http://{s}.tile.thunderforest.com/spinal-map/{z}/{x}/{y}.png'

    map_params = {'named_map_name': self.get_carto_namedmap(),
                  'basemap': new_basemap,
                  'tablename': self.get_carto_tablename(),
                  'cartocss': cartocss}

    bounds = self.get_bounds()
    args = dict(map_params, **bounds)
    new_template = get_named_map_template() % args
    if debug: print(new_template)
    endpoint = ("https://eschbacher.carto.com/api/v1/map/named/"
                "{map_name}?api_key={api_key}").format(
                    map_name=self.get_carto_namedmap(),
                    api_key=self.get_carto_api_key())

    resp = requests.put(endpoint,
                        data=new_template,
                        headers={'content-type': 'application/json'})
    # print(resp.status_code)
    # TODO: replace with bounding box extent instead
    #       do this in the map creation/updating?
    # https://carto.com/docs/carto-engine/maps-api/named-maps#arguments
    img = ("http://{username}.carto.com/api/v1/map/static/named/"
           "{map_name}/400/400.png")

    # print("response: {}".format(resp))
    if resp.status_code == requests.codes.ok:
        return img.format(username=self.get_carto_username(),
                          map_name=self.get_carto_namedmap())
    else:
        resp.raise_for_status()

pd.DataFrame.get_static_snapshot = get_static_snapshot
pd.DataFrame.get_bounds = get_bounds


def get_named_map_template():
    """

    """

    template = '''{
      "version": "0.0.1",
      "name": "%(named_map_name)s",
      "auth": {
        "method": "open"
      },
      "placeholders": {
      },
      "view": {
        "bounds": {
          "west": %(west)s,
          "south": %(south)s,
          "east": %(east)s,
          "north": %(north)s
        }
      },
      "layergroup": {
        "version": "1.3.0",
        "layers": [
          {
            "type": "http",
            "options": {
              "urlTemplate": "%(basemap)s",
              "subdomains": [
                "a",
                "b",
                "c"
              ]
            }
          },
          {
            "type": "mapnik",
            "options": {
              "sql": "select * from %(tablename)s",
              "cartocss": "%(cartocss)s",
              "cartocss_version": "2.3.0"
            }
          }
        ]
      }
    }'''
    return template
