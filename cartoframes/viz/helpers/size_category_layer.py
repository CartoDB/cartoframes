from __future__ import absolute_import

from ..layer import Layer


def size_category_layer(source, value, title='', top=5, cat=None, size=None, color=None):
    """Helper function for quickly creating a size category layer.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by
        title (str, optional): Title of legend
        top (int, optional): Number of size categories for layer. Default is
          5. Valid values range from 1 to 16.
        cat (str, optional): Category list. Must be a valid CARTO VL category
          list.
        size (str, optiona): Min/max size array in CARTO VL syntax. Default is
          '[2, 20]' for point geometries and '[1, 10]' for lines.
        color (str, optional): Hex value, rgb expression, or other valid
          CARTO VL color. Default is '#F46D43' for point geometries and
          '#4CC8A3' for lines.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`. Includes Legend and
        popup on `value`.
    """
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
            'type': {
                'point': 'size-category-point',
                'line': 'size-category-line',
                'polygon': 'size-category-polygon'
            },
            'title': title or value,
            'description': ''
        }
    )
