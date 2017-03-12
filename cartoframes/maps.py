"""
Functions and methods for interactive and static maps
"""

import pandas as pd

def create_named_map(username, api_key, tablename):
    """Create a default named map for later use

    :param username: CARTO username
    :type username: string
    :param api_key: CARTO API key
    :type api_key: string
    :param tablename: Table in user account to create a map from
    :type tablename: string
    """
    import json
    from time import time
    import requests

    map_name = '{table}_{time}'.format(table=tablename,
                                       time=str(time()).replace('.', '_'))

    defaults = {'named_map_name': map_name,
                'basemap': ('https://cartodb-basemaps-{s}.global.ssl.fastly'
                            '.net/dark_all/{z}/{x}/{y}.png'),
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
    resp = requests.post(api_endpoint,
                         data=filled_template,
                         headers={'content-type': 'application/json'})
    if resp.status_code == requests.codes.ok:
        return json.loads(resp.text)['template_id']
    else:
        resp.raise_for_status()

    return None


def get_bounds(self, debug=False):
    """Get the southwestern most point, and northeastern most point

    :returns: Dictionary with the following keys:
        * ``west``: longitude of the western-most extent
        * ``south``: latitutde of the southern-most extent
        * ``east``: longitude of the eastern-most extent
        * ``north``: latitutde of the northern-most extent
    """

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


def _get_static_snapshot(self, cartocss, basemap, figsize=(647, 400),
                         debug=False):
    """Update a named map with a new configuration.

    :param cartocss: CartoCSS to define new map style
    :type cartocss: string
    :param basemap: Basemap XYZ template to include in new map style
    :type basemap: string
    :param figsize: (Optional) Dimensions of output image (width, height) as a tuple
    :type figsize: tuple of integers

    :returns: URL to newly updated image
    :rtype: string
    """
    import requests
    if basemap:
        new_basemap = basemap
    else:
        new_basemap = ('https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
                       'dark_all/{z}/{x}/{y}.png')

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
           "{map_name}/{width}/{height}.png")

    if resp.status_code == requests.codes.ok:
        return img.format(username=self.get_carto_username(),
                          map_name=self.get_carto_namedmap(),
                          width=figsize[0],
                          height=figsize[1])
    else:
        resp.raise_for_status()

pd.DataFrame._get_static_snapshot = _get_static_snapshot
pd.DataFrame.get_bounds = get_bounds


def get_named_map_template():
    """Return named map template. See CARTO's Maps API documentation for more information: https://carto.com/docs/carto-engine/maps-api/named-maps

    :returns: named map template, with values to be filled in
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


def get_named_mapconfig(username, mapname):
    """Named Maps API template for carto.js

    :param username: The username of the CARTO account
    :param mapname: The mapname a cartoframe is associated with CARTO account

    :returns: mapconfig object for a named map as serialized JSON
    """
    map_args = {'mapname': mapname,
                'username': username}

    mapconfig = '''{
      "user_name": "%(username)s",
      "type": "namedmap",
      "named_map": {
        "name": "%(mapname)s"
      },
      "subdomains": [ "a", "b", "c" ]
      }''' % map_args
    return mapconfig
