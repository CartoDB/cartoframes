from ..style import Style
from ..helpers.utils import get_value


def size_bins_style(
        value, method='quantiles', bins=5, breaks=None, size=None, color=None,
        opacity=None, stroke_width=None, stroke_color=None, animate=None):
    """Helper function for quickly creating a size bind style with
    classification method/buckets.

    Args:
        value (str): Column to symbolize by.
        method (str, optional): Classification method of data: "quantiles", "equal", "stdev".
          Default is "quantiles".
        bins (int, optional): Number of size classes (bins) for map. Default is 5.
        breaks (list<int>, optional): Assign manual class break values.
        size (int, optional): Min/max size array in CARTO VL syntax. Default is
          '[2, 14]' for point geometries and '[1, 10]' for lines.
        color (str, optional): Hex value, rgb expression, or other valid
          CARTO VL color. Default is '#EE5D5A' for point geometries and
          '#4CC8A3' for lines.
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
    else:
        func = 'buckets'
        breaks = list(breaks)

    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'

    if opacity is None:
        opacity = '0.8'

    return Style({
        'point': {
            'width': 'ramp({0}(${1}, {2}), {3})'.format(
                func, value, breaks or bins, size or [2, 14]),
            'color': 'opacity({0}, {1})'.format(
                color or '#EE4D5A', opacity),
            'strokeColor': get_value(stroke_color, 'point', 'strokeColor'),
            'strokeWidth': get_value(stroke_width, 'point', 'strokeWidth'),
            'filter': animation_filter
        },
        'line': {
            'width': 'ramp({0}(${1}, {2}), {3})'.format(
                func, value, breaks or bins, size or [1, 10]),
            'color': 'opacity({0}, {1})'.format(
                color or '#4CC8A3', opacity),
            'filter': animation_filter
        }
    })
