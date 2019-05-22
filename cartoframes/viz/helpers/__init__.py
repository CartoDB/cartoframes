from __future__ import absolute_import

from ..layer import Layer


def inspect(helper):
    import inspect
    lines = inspect.getsource(helper)
    print(lines)


def color_category_layer(source, category, top=11, palette='bold'):
    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp(top(${0}, {1}), {2})'.format(category, top, palette)
            },
            'line': {
                'color': 'ramp(top(${0}, {1}), {2})'.format(category, top, palette)
            },
            'polygon': {
                'color': 'opacity(ramp(top(${0}, {1}), {2}),0.9)'.format(category, top, palette)
            }
        },
        popup={
            'hover': [{
                'label': category,
                'value': '$' + category
            }]
        },
        legend={
            'type': 'basic',
            'ramp': 'color',
            'heading': category,
            'description': ''
        }
    )


def color_bins_layer(source, number, bins=5, palette='reverse(purpor)'):
    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp(globalQuantiles(${0},{1}), {2})'.format(number, bins, palette)
            },
            'line': {
                'color': 'ramp(globalQuantiles(${0},{1}), {2})'.format(number, bins, palette)
            },
            'polygon': {
                'color': 'opacity(ramp(globalQuantiles(${0},{1}), {2}),0.9)'.format(number, bins, palette)
            }
        },
        popup={
            'hover': [{
                'label': number,
                'value': '$' + number
            }]
        },
        legend={
            'type': 'basic',
            'ramp': 'color',
            'heading': number,
            'description': ''
        }
    )
