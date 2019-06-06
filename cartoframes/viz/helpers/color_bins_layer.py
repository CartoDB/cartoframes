from __future__ import absolute_import

from ..layer import Layer


def color_bins_layer(source, value, title='', bins=5, palette='purpor'):
    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp(globalQuantiles(${0}, {1}), reverse({2}))'.format(value, bins, palette)
            },
            'line': {
                'color': 'ramp(globalQuantiles(${0}, {1}), reverse({2}))'.format(value, bins, palette)
            },
            'polygon': {
                'color': 'opacity(ramp(globalQuantiles(${0}, {1}), reverse({2})), 0.9)'.format(value, bins, palette)
            }
        },
        popup={
            'hover': {
                'title': title or value,
                'value': '$' + value
            }
        },
        legend={
            'type': 'color-bins',
            'prop': 'color',
            'title': title or value,
            'description': ''
        }
    )
