from ..style import Style
from ..helpers.utils import serialize_palette, get_value


def color_continuous_style(
        value, range_min=None, range_max=None, palette=None, size=None, opacity=None,
        stroke_color=None, stroke_width=None, animate=None):
    """Helper function for quickly creating a color continuous style.

    Args:
        value (str): Column to symbolize by.
        range_min (int, optional): The minimum value of the data range for the continuous
          color ramp. Defaults to the globalMIN of the dataset.
        range_max (int, optional): The maximum value of the data range for the continuous
          color ramp. Defaults to the globalMAX of the dataset.
        palette (str, optional): Palette that can be a named cartocolor palette
          or other valid color palette. Use `help(cartoframes.viz.color_palettes)` to
          get more information. Default is "bluyl".
        size (int, optional): Size of point or line features.
        opacity (int, optional): Opacity value for point color and line features.
          Default is '0.8'.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
          Default is '#222'.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        :py:class:`Style <cartoframes.viz.Style>`
    """
    default_palette = 'bluyl'
    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'

    if range_min is None:
        range_min = 'globalMIN(${0})'.format(value)

    if range_max is None:
        range_max = 'globalMAX(${0})'.format(value)

    return Style({
        'point': {
            'color': 'opacity(ramp(linear(${0}, {1}, {2}), {3}), {4})'.format(
                value, range_min, range_max,
                serialize_palette(palette) or default_palette,
                get_value(opacity, 'point', 'opacity')
            ),
            'width': get_value(size, 'point', 'width'),
            'strokeColor': get_value(stroke_color, 'point', 'strokeColor'),
            'strokeWidth': get_value(stroke_width, 'point', 'strokeWidth'),
            'filter': animation_filter
        },
        'line': {
            'color': 'opacity(ramp(linear(${0}, {1}, {2}), {3}), {4})'.format(
                value, range_min, range_max,
                serialize_palette(palette) or default_palette,
                get_value(opacity, 'line', 'opacity')
            ),
            'width': get_value(size, 'line', 'width'),
            'filter': animation_filter
        },
        'polygon': {
            'color': 'opacity(ramp(linear(${0}, {1}, {2}), {3}), {4})'.format(
                value, range_min, range_max,
                serialize_palette(palette) or default_palette,
                get_value(opacity, 'polygon', 'opacity')
            ),
            'strokeColor': get_value(stroke_color, 'polygon', 'strokeColor'),
            'strokeWidth': get_value(stroke_width, 'polygon', 'strokeWidth'),
            'filter': animation_filter
        }
    })
