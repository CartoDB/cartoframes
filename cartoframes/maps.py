"""Utilities for creating map templates for CARTO's Named Maps API"""
import json


def non_basemap_layers(layers):
    """Retrieve all map layers which are not basemaps"""
    return [layer for layer in layers if not layer.is_basemap]

def top_basemap_layer_url(layers):
    """Returns the URL of the top map layer if it exists"""
    if layers[-1].is_basemap and len(layers) > 1:
        return layers[-1].url
    return None

def has_time_layer(layers):
    """Returns `True` if there is a time/torque layer in `layers.
    Returns `False` otherwise"""
    return any(layer.time for layer in layers if not layer.is_basemap)


def get_map_name(layers, has_zoom):
    """Creates a map named based on supplied parameters"""
    version = '20170406'
    num_layers = len(non_basemap_layers(layers))
    has_labels = len(layers) > 1 and layers[-1].is_basemap
    has_time = has_time_layer(layers)
    basemap_id = dict(light=0, dark=1, voyager=2)[layers[0].source]

    return ('cartoframes_ver{version}'
            '_layers{layers}'
            '_time{has_time}'
            '_baseid{baseid}'
            '_labels{has_labels}'
            '_zoom{has_zoom}').format(
                version=version,
                layers=num_layers,
                has_time=('1' if has_time else '0'),
                # TODO: Remove this once baselayer urls can be passed in named
                #       map config
                baseid=basemap_id,
                has_labels=('1' if has_labels else '0'),
                has_zoom=('1' if has_zoom else '0')
            )


def get_map_template(layers, has_zoom):
    """Creates a map template based on custom parameters supplied"""
    num_layers = len(non_basemap_layers(layers))
    has_time = has_time_layer(layers)
    name = get_map_name(layers, has_zoom=has_zoom)

    # Add basemap layer
    layers_field = [{
        'type': 'http',
        'options': {
            # TODO: Remove this once baselayer urls can be passed in named map
            #       config
            'urlTemplate': layers[0].url,
            # 'urlTemplate': '<%= basemap_url %>',
            'subdomains': "abcd",
        },
    }]

    # [BUG] Remove this once baselayer urls can be passed in named map config
    placeholders = {}
    # placeholders = {
    #     'basemap_url': {
    #         'type': 'sql_ident',
    #         'default': ('https://cartodb-basemaps-{s}.global.ssl.fastly.net/'
    #                     'dark_all/{z}/{x}/{y}.png'),
    #     },
    # }

    for idx in range(num_layers):
        layers_field.extend([{
            'type': ('torque' if (has_time and idx == (num_layers - 1))
                     else 'mapnik'),
            'options': {
                'cartocss_version': '2.1.1',
                'cartocss': '<%= cartocss_{idx} %>'.format(idx=idx),
                'sql': '<%= sql_{idx} %>'.format(idx=idx),
                # [BUG] No [] for templating
                # 'interactivity': '<%= interactivity_{idx} %>'.format(
                #                                                 idx=idx),
            }
        }])
        placeholders.update({
            'cartocss_{idx}'.format(idx=idx): {
                'type': 'sql_ident',
                'default': ('#layer {'
                            ' marker-fill: red;'
                            ' marker-width: 5;'
                            ' marker-allow-overlap: true;'
                            ' marker-line-color: #000; }'),
            },
            'sql_{idx}'.format(idx=idx): {
                'type': 'sql_ident',
                'default': (
                        "SELECT "
                        "ST_PointFromText('POINT(0 0)', 4326) AS the_geom, "
                        "1 AS cartodb_id, "
                        "ST_PointFromText('Point(0 0)', 3857) AS "
                        "the_geom_webmercator"
                    ),
            },
            # [BUG] No [] for templating
            # 'interactivity_{idx}'.format(idx=idx): {
            #     'type': 'sql_ident',
            #     'default': '["cartodb_id"]',
            # },
        })

    # Add labels if they're in front
    if num_layers > 0 and layers[-1].is_basemap:
        layers_field.extend([{
            'type': 'http',
            'options': {
                # TODO: Remove this once baselayer urls can be passed in named
                #       map config
                'urlTemplate': layers[-1].url,
                # 'urlTemplate': '<%= basemap_url %>',
                'subdomains': "abcd",
            },
        }])

    if has_zoom:
        view = {
            'zoom': '<%= zoom %>',
            'center': {
                'lng': '<%= lng %>',
                'lat': '<%= lat %>',
            },
        }
        placeholders.update({
            'zoom': {
                'type': 'number',
                'default': 3,
            },
            'lng': {
                'type': 'number',
                'default': 0,
            },
            'lat': {
                'type': 'number',
                'default': 0,
            },
        })
    else:
        view = {
            'bounds': {
                'west': '<%= west %>',
                'south': '<%= south %>',
                'east': '<%= east %>',
                'north': '<%= north %>',
            },
        }
        placeholders.update({
            'west': {
                'type': 'number',
                'default': -45,
            },
            'south': {
                'type': 'number',
                'default': -45,
            },
            'east': {
                'type': 'number',
                'default':  45,
            },
            'north': {
                'type': 'number',
                'default':  45,
            },
        })

    return json.dumps({
        'version': '0.0.1',
        'name': name,
        'placeholders': placeholders,
        'layergroup': {
            'version': '1.0.1',
            'layers': layers_field,
        },
        'view': view,
    })
