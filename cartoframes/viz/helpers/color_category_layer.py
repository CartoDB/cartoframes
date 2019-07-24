from __future__ import absolute_import

from .utils import serialize_palette

from ..layer import Layer


def color_category_layer(
        source, value, title='', top=11, cat=None,
        palette=None, description='', footer='',
        legend=True, popup=True, widget=False, animate=None):
    """Helper function for quickly creating a category color map.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend.
        top (int, optional): Number of category for map. Default is 11. Values
          can range from 1 to 16.
        cat (str, optional): Category list. Must be a valid CARTO VL category
          list.
        palette (str, optional): Palette that can be a named CARTOColor palette
          or other valid CARTO VL palette expression. Default is `bold`.
        description (str, optional): Description text legend placed under legend title.
        footer (str, optional): Footer text placed under legend items.
        legend (bool, optional): Display map legend: "True" or "False".
          Set to "True" by default.
        popup (bool, optional): Display popups on hover and click: "True" or "False".
          Set to "True" by default.
        widget (bool, optional): Display a widget for mapped data.
          Set to "False" by default.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`.
        Includes a legend, popup and widget on `value`.
    """
    func = 'buckets' if cat else 'top'
    default_palette = 'bold'
    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'

    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp({0}(${1}, {2}), {3})'.format(
                    func, value, cat or top, serialize_palette(palette) or default_palette),
                'filter': animation_filter
            },
            'line': {
                'color': 'ramp({0}(${1}, {2}), {3})'.format(
                    func, value, cat or top, serialize_palette(palette) or default_palette),
                'filter': animation_filter
            },
            'polygon': {
                'color': 'opacity(ramp({0}(${1}, {2}), {3}), 0.9)'.format(
                    func, value, cat or top, serialize_palette(palette) or default_palette),
                'filter': animation_filter
            }
        },
        popup=popup and not animate and {
            'hover': {
                'title': title or value,
                'value': '$' + value
            }
        },
        legend=legend and {
            'type': {
                'point': 'color-category-point',
                'line': 'color-category-line',
                'polygon': 'color-category-polygon'
            },
            'title': title or value,
            'description': description,
            'footer': footer
        },
        widgets=[
            animate and {
                'type': 'time-series',
                'value': animate,
                'title': 'Animation'
            },
            widget and {
                'type': 'category',
                'value': value,
                'title': 'Categories'
            }
        ]
    )
