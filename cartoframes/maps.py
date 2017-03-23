"""
Functions and methods for interactive and static maps
"""


def create_named_map(baseurl, api_key, tablename):
    """Create a default named map for later use

    :param baseurl: Base URL for API calls
    :type baseurl: string
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
                'basemap_layer': basemap_config(
                    'https://cartodb-basemaps-{s}.global'
                    '.ssl.fastly.net/dark_all/{z}/{x}/{y}.png'),
                'cartocss': '#layer{ marker-width: 7; marker-fill: #00F; }',
                'tablename': tablename,
                'west': -45,
                'south': -45,
                'east': 45,
                'north': 45,
                'labels': ''}

    filled_template = get_named_map_template() % defaults

    api_endpoint = ('{baseurl}v1/map/named'
                    '?api_key={api_key}').format(baseurl=baseurl,
                                                 api_key=api_key)
    resp = requests.post(api_endpoint,
                         data=filled_template,
                         headers={'Content-Type': 'application/json'})
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
                         center=None, zoom=None, debug=False):
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
    try:
        # if python3
        from urllib.parse import urlencode
    except ImportError:
        # if python2
        from urllib import urlencode

    if isinstance(basemap, list) and len(basemap) == 2:
        baselayer = basemap[0]
        labels = basemap[1]
    else:
        baselayer = basemap
        labels = None

    map_params = {'named_map_name': self.get_carto_namedmap(),
                  'basemap_layer': basemap_config(baselayer),
                  'tablename': self.get_carto_tablename(),
                  'labels': (',' + basemap_config(labels)) if labels else '',
                  'cartocss': cartocss}

    bounds = self.get_bounds()
    args = dict(map_params, **bounds)
    new_template = get_named_map_template() % args
    if debug: print(new_template)
    endpoint = "{baseurl}v1/map/named/{mapname}?api_key={api_key}".format(
        baseurl=self.get_carto_baseurl(),
        mapname=self.get_carto_namedmap(),
        api_key=self.get_carto_api_key())

    resp = requests.put(endpoint,
                        data=new_template,
                        headers={'Content-Type': 'application/json'})
    # TODO: replace with bounding box extent instead
    #       do this in the map creation/updating?
    # https://carto.com/docs/carto-engine/maps-api/named-maps#arguments

    if resp.status_code == requests.codes.ok:
        mapview = {}
        if zoom:
            mapview['zoom'] = zoom
        if center:
            mapview['lon'] = center[0]
            mapview['lat'] = center[1]

        img = ("{baseurl}v1/map/static/named/"
               "{map_name}/{width}/{height}.png"
               "?{mapview}")

        return img.format(baseurl=self.get_carto_baseurl(),
                          map_name=self.get_carto_namedmap(),
                          width=figsize[0],
                          height=figsize[1],
                          mapview=urlencode(mapview))
    else:
        resp.raise_for_status()


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
          %(basemap_layer)s,
          {
            "type": "mapnik",
            "options": {
              "sql": "select * from %(tablename)s",
              "cartocss": "%(cartocss)s",
              "cartocss_version": "2.3.0"
            }
          }%(labels)s
        ]
      }
    }'''
    return template

def basemap_config(basemap_url):
    template = '''
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
          }
    '''
    return template % {'basemap': basemap_url}


def get_named_mapconfig(username, mapname, baseurl=None):
    """Named Maps API template for carto.js

    :param username: The username of the CARTO account
    :type username: string
    :param mapname: The mapname a cartoframe is associated with CARTO account
    :type mapname: string
    :param baseurl: Base URL for API calls
    :type username: string

    :returns: mapconfig object for a named map as serialized JSON
    :rtype: string
    """
    import sys
    if sys.version_info[0] == 3:
        from urllib.parse import urlparse
    else:
        from urlparse import urlparse

    map_args = {'mapname': mapname,
                'username': username}
    if baseurl:
        if baseurl.endswith('/api/'):
            map_args['baseurl'] = baseurl[:-5]
        else:
            map_args['baseurl'] = baseurl
    else:
        map_args['baseurl'] = 'https://{username}.carto.com/'.format(
            username=username)

    if urlparse(baseurl).netloc.endswith('.carto.com/'):
        map_args['domain'] = 'carto.com'
    else:
        map_args['domain'] = urlparse(baseurl).netloc

    # questions:
    # 1. should tiler protocol always be http or https? what would require us to change it? on prem vs. carto org user vs. carto single account user vs. ...
    # 2. for the tiler_protocol, can we reuse the format for maps_api_template or do i need to strip out the domains
    # 3. it all should work fine with named maps?
    mapconfig = '''{{
      "user_name": "{username}",
      "maps_api_template": "{baseurl}",
      "sql_api_template": "{baseurl}",
      "tiler_protocol": "https",
      "tiler_domain": "{domain}",
      "tiler_port": "80",
      "type": "namedmap",
      "named_map": {{
        "name": "{mapname}"
      }},
      "subdomains": [ "a", "b", "c" ]
      }}'''.format(**map_args)
    return mapconfig


def get_basemap(self, options):
    """
    :param options: This can be one of the following:

    * XYZ URL for a custom basemap. See https://leaflet-extras.github.io/leaflet-providers/preview/ for examples.
    * CARTO basemap style

      - Specific description: `light_all`, `light_nolabels`, `dark_all`, or `dark_nolabels`
      - General descrption: `light` or `dark`. Specifying one of these results in the best basemap for the map geometries.

    * Dictionary with the following keys:

      - `style`: (required) descrption of the map type (`light` or `dark`)
      - `labels`: (optional) Show labels (`True`) or not (`False`). If this option is not included, the best basemap will be chosen based on what was entered for `style` and the geometry type of the basemap.

    :type options: string or dict

    :returns: basemap(s) URLs given the input parameters
    :rtype: string or list
    """

    template = ('http://cartodb-basemaps-{{s}}.global.ssl.fastly.net/'
                '{style}/{{z}}/{{x}}/{{y}}.png')
    style_options = ('light_all', 'dark_all', 'light_nolabels',
                     'dark_nolabels',)
    label_options = ('dark', 'light',)

    if isinstance(options, str):
        if options[0:4] == 'http':
            # input is already a basemap
            return (options, None)
        elif options in style_options:
            # choose one of four carto types
            return (template.format(style=options),
                    'dark' if 'dark_' in options else 'light')
        elif options in ('light', 'dark'):
            if self.get_carto_geomtype() in ('point', 'line'):
                return (template.format(style=options + '_all'),
                        options)
            else:
                return [template.format(style=options + '_nolabels'),
                        template.format(style=options + '_only_labels')], options
        else:
            raise ValueError("Text inputs must be an XYZ basemap format, or "
                             "one of: {}.".format(','.join(style_options)))
    elif (isinstance(options, dict) and
          'style' in options and
          options['style'] in label_options):
        if ('labels' in options and
                options['labels'] is True):
            return ([template.format(style=options['style'] + '_nolabels'),
                     template.format(style=options['style'] + '_only_labels')],
                    options['style'])
        elif ('labels' in options and options['labels'] is False):
            return (template.format(style=options['style'] + '_nolabels'),
                    options['style'])
        else:
            if self.get_carto_geomtype() in ('point', 'line'):
                return (template.format(style=options['style'] + '_all'),
                        options['style'])
            else:
                return [template.format(style=options['style'] + '_nolabels'),
                        template.format(style=options['style'] + '_only_labels')], options['style']
    else:
        if self.get_carto_geomtype() in ('point', 'line'):
            return (template.format(style='dark_all'),
                    'dark')
        elif self.get_carto_geomtype() == 'polygon':
            return ([template.format(style='dark_all'),
                    template.format(style='dark_only_labels')],
                    'dark')
        else:
            return (template.format(style='dark_all'),
                    'dark')
    return None
