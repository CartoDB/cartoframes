from ..style import Style
from ..helpers.utils import serialize_palette, get_value


def color_bins_style(
        value, method='quantiles', bins=5, breaks=None, palette=None, size=None,
        opacity=None, stroke_color=None, stroke_width=None, animate=None):
    """Helper function for quickly creating a color bins style.

    Args:
        value (str): Column to symbolize by.
        method (str, optional): Classification method of data: "quantiles", "equal", "stdev".
          Default is "quantiles".
        bins (int, optional): Number of size classes (bins) for map. Default is 5.
        breaks (list<int>, optional): Assign manual class break values.
        palette (str, optional): Palette that can be a named cartocolor palette
          or other valid color palette. Use `help(cartoframes.viz.color_palettes)` to
          get more information. Default is "purpor".
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
    if method not in ('quantiles', 'equal', 'stdev'):
        raise ValueError('Available methods are: "quantiles", "equal", "stdev".')

    if breaks is None:
        func = {
            'quantiles': 'globalQuantiles',
            'equal': 'globalEqIntervals',
            'stdev': 'globalStandardDev'
        }.get(method)
        default_palette = {
            'quantiles': 'purpor',
            'equal': 'purpor',
            'stdev': 'temps'
        }.get(method)
    else:
        func = 'buckets'
        default_palette = 'purpor'
        breaks = list(breaks)

    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'

    return Style({
        'point': {
            'color': 'opacity(ramp({0}(${1}, {2}), {3}),{4})'.format(
                func, value, breaks or bins,
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
                func, value, breaks or bins,
                serialize_palette(palette) or default_palette,
                get_value(opacity, 'line', 'opacity')
            ),
            'width': get_value(size, 'line', 'width'),
            'filter': animation_filter
        },
        'polygon': {
            'color': 'opacity(ramp({0}(${1}, {2}), {3}), {4})'.format(
                func, value, breaks or bins,
                serialize_palette(palette) or default_palette,
                get_value(opacity, 'polygon', 'opacity')
            ),
            'strokeColor': get_value(stroke_color, 'polygon', 'strokeColor'),
            'strokeWidth': get_value(stroke_width, 'polygon', 'strokeWidth'),
            'filter': animation_filter
        }
    })
