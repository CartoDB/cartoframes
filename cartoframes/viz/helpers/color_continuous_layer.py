from __future__ import absolute_import

from ..layer import Layer


def color_continuous_layer(source, value, title='', palette=None):
    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp(linear(${0}), {1})'.format(value, palette or 'bluyl')
            },
            'line': {
                'color': 'ramp(linear(${0}), {1})'.format(value, palette or 'bluyl')
            },
            'polygon': {
                'color': 'opacity(ramp(linear(${0}), {1}), 0.9)'.format(value, palette or 'bluyl')
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
                'point': 'color-continuous-point',
                'line': 'color-continuous-line',
                'polygon': 'color-continuous-polygon'
            },
            'title': title or value,
            'description': ''
        }
    )
