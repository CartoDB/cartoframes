import json


def non_basemap_layers(layers):
    return [layer for layer in layers if not layer.is_basemap]


def has_time_layer(layers):
    return any(layer.time for layer in layers if not layer.is_basemap)


def get_map_name(layers, *, has_zoom):
    version    = '20170406'
    num_layers = len(non_basemap_layers(layers))
    has_labels = num_layers > 1 and layers[-1].is_basemap
    has_time   = has_time_layer(layers)

    return ('cartoframes_ver{version}_layers{layers}'
            '_time{has_time}_labels{has_labels}_zoom{has_zoom}').format(
                version=version,
                layers=num_layers,
                has_time=('1' if has_time else '0'),
                has_labels=('1' if has_labels else '0'),
                has_zoom=('1' if has_zoom else '0')
            )


def get_map_template(layers, *, has_zoom):
    num_layers = len(non_basemap_layers(layers))
    has_time   = has_time_layer(layers)
    name = get_map_name(layers, has_zoom=has_zoom)

    layers_field = [{
        'type': 'torque' if (has_time and idx == (num_layers - 1)) else 'mapnik',
        'options': {
            'cartocss_version': '2.1.1',
            'cartocss': '<%= cartocss_{idx} %>'.format(idx=idx),
            'sql': '<%= sql_query_{idx} %>'.format(idx=idx),
        }
    } for idx in range(num_layers)]

    if has_zoom:
        view = {
            'zoom': '<%= zoom %>',
            'center': {
                'lng': '<%= lng %>',
                'lat': '<%= lat %>',
            },
        }
    else:
        view = {
            'bounds': {
                'west' : '<%= west %>',
                'south': '<%= south %>',
                'east' : '<%= east %>',
                'north': '<%= north %>',
            },
        }

    return json.dumps({
        'version': '0.0.1',
        'name': name,
        'layergroup': {
            'version': '1.0.1',
            'layers': layers_field,
        },
        'view': view,
    })