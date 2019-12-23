from ..style import Style
from ..helpers.utils import get_value


def size_continuous_style(
        value, range_min=None, range_max=None, size=None, color=None, opacity=None,
        stroke_width=None, stroke_color=None, animate=None, credentials=None):
    """Helper function for quickly creating a size continuous style.

    Args:
        value (str): Column to symbolize by.
        range_min (int, optional): The minimum value of the data range for the continuous
          size ramp. Defaults to the globalMIN of the dataset.
        range_max (int, optional): The maximum value of the data range for the continuous
          size ramp. Defaults to the globalMAX of the dataset.
        size (str, optional): Min/max size array as a string. Default is
          '[2, 40]' for point geometries and '[1, 10]' for lines.
        color (str, optional): hex, rgb or named color value.
          Defaults is '#FFB927' for point geometries and '#4CC8A3' for lines.
        opacity (int, optional): Opacity value for point color and line features.
          Default is '0.8'.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
          Default is '#222'.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        :py:class:`Style <cartoframes.viz.Style>`
    """
    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'

    if range_min is None:
        range_min = 'globalMIN(${0})'.format(value)

    if range_max is None:
        range_max = 'globalMAX(${0})'.format(value)

    if opacity is None:
        opacity = '0.8'

    style = {
        'point': {
            '@width_value': 'ramp(linear(${0}, {1}, {2}), {3})'.format(
                value, range_min, range_max, size or [2, 40]),
            'width': 'ramp(linear(sqrt(${0}), sqrt({1}), sqrt({2})), {3})'.format(
                value, range_min, range_max, size or [2, 40]),
            'color': 'opacity({0}, {1})'.format(
                color or '#FFB927', opacity),
            'strokeColor': get_value(stroke_color, 'point', 'strokeColor'),
            'strokeWidth': get_value(stroke_width, 'point', 'strokeWidth'),
            'filter': animation_filter
        },
        'line': {
            '@width_value': 'ramp(linear(${0}, {1}, {2}), {3})'.format(
                value, range_min, range_max, size or [1, 10]),
            'width': 'ramp(linear(${0}, {1}, {2}), {3})'.format(
                value, range_min, range_max, size or [1, 10]),
            'color': 'opacity({0}, {1})'.format(
                color or '#4CC8A3', opacity),
            'filter': animation_filter
        }
    }

    return Style('size-continuous', value, style)
