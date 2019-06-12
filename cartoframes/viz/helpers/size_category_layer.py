from __future__ import absolute_import

from ..layer import Layer


def size_category_layer(source, value, title='', top=5, cat=None, size=None, color=None):
    func = 'buckets' if cat else 'top'
    return Layer(
        source,
        style={
            'point': {
                'width': 'ramp({0}(${1}, {2}), {3})'.format(func, value, cat or top, size or [2, 20]),
                'color': 'opacity({0}, 0.8)'.format(color or '#F46D43')
            },
            'line': {
                'width': 'ramp({0}(${1}, {2}), {3})'.format(func, value, cat or top, size or [1, 10]),
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
            'type': 'size-category',
            'title': title or value,
            'description': ''
        }
    )
