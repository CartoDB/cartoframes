from .utils import get_value
from ..style import Style


def size_category_style(
        value, top=5, cat=None,  ranges=None, color=None, opacity=None,
        stroke_width=None, stroke_color=None, animate=None):
    """Helper function for quickly creating a size category style.

    Args:
        value (str): Column to symbolize by.
        top (int, optional): Number of size categories. Default is 5. Values
          can range from 1 to 16.
        cat (list<str>, optional): Category list as a string.
        ranges (str, optional): Min/max size array as a string. Default is
          '[2, 20]' for point geometries and '[1, 10]' for lines.
        color (str, optional): hex, rgb or named color value.
          Default is '#F46D43' for point geometries and '#4CC8A3' for lines.
        opacity (int, optional): Opacity value for point color and line features.
          Default is '0.8'.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
          Default is '#222'.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        :py:class:`Style <cartoframes.viz.Style>`
    """

    func = 'buckets' if cat else 'top'
    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'
    opacity = opacity if opacity else '0.8'

    style = {
        'point': {
            'color': 'opacity({0}, {1})'.format(
                get_value(color, 'color', 'point'),
                get_value(opacity, 1)),
            'width': 'ramp({0}(${1}, {2}), {3})'.format(
                func, value, cat or top, ranges or [2, 20]),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'point'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'point'),
            'filter': animation_filter
        },
        'line': {
            'color': 'opacity({0}, {1})'.format(
                get_value(color, 'color', 'line'),
                get_value(opacity, 1)),
            'width': 'ramp({0}(${1}, {2}), {3})'.format(
                func, value, cat or top, ranges or [1, 10]),
            'filter': animation_filter
        }
    }

    return Style('size-category', value, style)
