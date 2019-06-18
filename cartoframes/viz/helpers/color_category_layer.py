from __future__ import absolute_import

from ..layer import Layer


def color_category_layer(source, value, title='', top=11, cat=None, palette='bold'):
    """Helper function for quickly creating a category color map.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by
        title (str, optional): Title of legend
        top (int, optional): Number of category for map. Default is 11. Values
          can range from 1 to 16.
        cat (str, optional): Category list. Must be a valid CARTO VL category
          list.
        palette (str, optional): Palette that can be a named cartocolor palette
          or other valid CARTO VL palette expression. Default is `bold`.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`. Includes Legend and
        popup on `value`.
    """
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
