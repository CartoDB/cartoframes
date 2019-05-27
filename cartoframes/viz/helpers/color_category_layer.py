from __future__ import absolute_import

from ..layer import Layer


def color_category_layer(source, value, top=11, palette='bold', title=''):
    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp(top(${0}, {1}), {2})'.format(value, top, palette)
            },
            'line': {
                'color': 'ramp(top(${0}, {1}), {2})'.format(value, top, palette)
            },
            'polygon': {
                'color': 'opacity(ramp(top(${0}, {1}), {2}), 0.9)'.format(value, top, palette)
            }
        },
        popup={
            'hover': {
                'label': title or value,
                'value': '$' + value
            }
        },
        legend={
            'type': 'basic',
            'ramp': 'color',
            'heading': title or value,
            'description': '',
            'othersLabel': 'Others'
        }
    )
