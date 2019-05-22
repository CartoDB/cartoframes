from __future__ import absolute_import

from ..layer import Layer


def color_bins_layer(source, number, bins=5, palette='reverse(purpor)', label=''):
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
                'label': label or number,
                'value': '$' + number
            }]
        },
        legend={
            'type': 'basic',
            'ramp': 'color',
            'heading': label or number,
            'description': ''
        }
    )
