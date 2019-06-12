from __future__ import absolute_import

from ..layer import Layer


def size_bins_layer(source, value, title='', bins=5, size=None, color=None):
    return Layer(
        source,
        style={
            'point': {
                'width': 'ramp(globalQuantiles(${0}, {1}), {2})'.format(value, bins, size or [2, 20]),
                'color': 'opacity({0}, 0.8)'.format(color or '#F46D43')
            },
            'line': {
                'width': 'ramp(globalQuantiles(${0}, {1}), {2})'.format(value, bins, size or [1, 10]),
                'color': 'opacity({0}, 0.8)'.format(color or '#4CC8A3')
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
                'point': 'size-bins-point',
                'line': 'size-bins-line',
                'polygon': 'size-bins-polygon'
            },
            'title': title or value,
            'description': ''
        }
    )
