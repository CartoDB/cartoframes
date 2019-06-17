from __future__ import absolute_import

from ..layer import Layer


def size_continuous_layer(source, value, title='', size=None, color=None):
    return Layer(
        source,
        style={
            'point': {
                'width': 'ramp(linear(sqrt(${0}), sqrt(globalMin(${0})), sqrt(globalMax(${0}))), {1})'.format(
                    value, size or [2, 40]),
                'color': 'opacity({0}, 0.8)'.format(color or '#FFB927'),
                'strokeColor': 'opacity(#222,ramp(linear(zoom(),0,18),[0,0.6]))'
            },
            'line': {
                'width': 'ramp(linear(${0}), {1})'.format(value, size or [1, 10]),
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
                'point': 'size-continuous-point',
                'line': 'size-continuous-line',
                'polygon': 'size-continuous-polygon'
            },
            'title': title or value,
            'description': ''
        }
    )
