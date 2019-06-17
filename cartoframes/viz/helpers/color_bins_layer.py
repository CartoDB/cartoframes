from __future__ import absolute_import

from ..layer import Layer


def color_bins_layer(source, value, title='', bins=5, palette=None):
    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp(globalQuantiles(${0}, {1}), {2})'.format(value, bins, palette or 'purpor')
            },
            'line': {
                'color': 'ramp(globalQuantiles(${0}, {1}), {2})'.format(value, bins, palette or 'purpor')
            },
            'polygon': {
                'color': 'opacity(ramp(globalQuantiles(${0}, {1}), {2}), 0.9)'.format(value, bins, palette or 'purpor')
            }
        },
        popup={
            'hover': {
                'title': title or value,
                'value': '$' + value
            }
        },
        legend={
            'type': {
                'point': 'color-bins-point',
                'line': 'color-bins-line',
                'polygon': 'color-bins-polygon'
            },
            'title': title or value,
            'description': ''
        }
    )
