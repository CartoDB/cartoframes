from __future__ import absolute_import

from ..layer import Layer


def color_category_layer(source, value, title='', top=11, cat=None, palette='bold'):
    func = 'buckets' if cat else 'top'
    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp({0}(${1}, {2}), {3})'.format(func, value, cat or top, palette)
            },
            'line': {
                'color': 'ramp({0}(${1}, {2}), {3})'.format(func, value, cat or top, palette)
            },
            'polygon': {
                'color': 'opacity(ramp({0}(${1}, {2}), {3}), 0.9)'.format(func, value, cat or top, palette)
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
                'point': 'color-category-point',
                'line': 'color-category-line',
                'polygon': 'color-category-polygon'
            },
            'title': title or value,
            'description': ''
        }
    )
