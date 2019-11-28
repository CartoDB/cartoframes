from __future__ import absolute_import

from .utils import serialize_palette, get_value, get_popup

from ..layer import Layer


def color_category_layer(
        source, value, title='', top=11, cat=None, palette=None,
        size=None, opacity=None, stroke_color=None, stroke_width=None,
        description='', footer='', legend=True, popup=True,
        widget=False, animate=None, credentials=None):
    """Helper function for quickly creating a category color map.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend.
        top (int, optional): Number of category for map. Default is 11. Values
          can range from 1 to 16.
        cat (list<str>, optional): Category list. Must be a valid list of categories.
        palette (str, optional): Palette that can be a named CARTOColor palette
          or other valid CARTO VL palette expression. Default is `bold`.
        size (int, optional): Size of point or line features.
        opacity (int, optional): Opacity value for point color and line features.
          Default is '0.8'.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
          Default is '#222'.
        description (str, optional): Description text legend placed under legend title.
        footer (str, optional): Footer text placed under legend items.
        legend (bool, optional): Display map legend: "True" or "False".
          Set to "True" by default.
        popup (bool, optional): Display popups on hover and click: "True" or "False".
          Set to "True" by default.
        widget (bool, optional): Display a widget for mapped data.
          Set to "False" by default.
        animate (str, optional): Animate features by date/time or other numeric field.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
          A Credentials instance. This is only used for the simplified Source API.
          When a :py:class:`Source <cartoframes.viz.Source>` is pased as source,
          these credentials is simply ignored. If not provided the credentials will be
          automatically obtained from the default credentials.

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
                'color': 'opacity(ramp({0}(${1}, {2}), {3}),{4})'.format(
                    func, value, cat or top,
                    serialize_palette(palette) or default_palette,
                    get_value(opacity, 'point', 'opacity')
                ),
                'width': get_value(size, 'point', 'width'),
                'strokeColor': get_value(stroke_color, 'point', 'strokeColor'),
                'strokeWidth': get_value(stroke_width, 'point', 'strokeWidth'),
                'filter': animation_filter
            },
            'line': {
                'color': 'opacity(ramp({0}(${1}, {2}), {3}),{4})'.format(
                    func, value, cat or top,
                    serialize_palette(palette) or default_palette,
                    get_value(opacity, 'line', 'opacity')
                ),
                'width': get_value(size, 'line', 'width'),
                'filter': animation_filter
            },
            'polygon': {
                'color': 'opacity(ramp({0}(${1}, {2}), {3}), {4})'.format(
                    func, value, cat or top,
                    serialize_palette(palette) or default_palette,
                    get_value(opacity, 'polygon', 'opacity')
                ),
                'strokeColor': get_value(stroke_color, 'polygon', 'strokeColor'),
                'strokeWidth': get_value(stroke_width, 'polygon', 'strokeWidth'),
                'filter': animation_filter
            }
        },
        popup=popup and not animate and get_popup(
          popup, title, value, value),
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
        ],
        credentials=credentials
    )
