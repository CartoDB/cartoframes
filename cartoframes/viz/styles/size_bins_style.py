from .utils import get_value, prop
from ..style import Style
from ..legends import size_bins_legend
from ..widgets import histogram_widget
from ..popups import popup_element


def size_bins_style(value, method='quantiles', bins=5, breaks=None, size_range=None, color=None,
                    opacity=None, stroke_width=None, stroke_color=None, animate=None):
    """Helper function for quickly creating a size bind style with
    classification method/buckets.

    Args:
        value (str): Column to symbolize by.
        method (str, optional): Classification method of data: "quantiles", "equal", "stdev".
            Default is "quantiles".
        bins (int, optional): Number of size classes (bins) for map. Default is 5.
        breaks (list<int>, optional): Assign manual class break values.
        size_range (list<int>, optional): Min/max size array as a string. Default is
            [2, 14] for point geometries and [1, 10] for lines.
        color (str, optional): Hex, rgb or named color value. Default is '#EE5D5A' for point geometries and
            '#4CC8A3' for lines.
        opacity (float, optional): Opacity value for point color and line features.
            Default is 0.8.
        stroke_color (str, optional): Color of the stroke on point features.
            Default is '#222'.
        stroke_width (int, optional): Size of the stroke on point features.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        cartoframes.viz.style.Style

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

    animation_filter = 'animation(linear({}), 20, fade(1,1))'.format(prop(animate)) if animate else '1'

    data = {
        'point': {
            'color': 'opacity({0}, {1})'.format(
                get_value(color, '#EE5D5A'),
                get_value(opacity, 0.8)),
            'width': 'ramp({0}({1}, {2}), {3})'.format(
                func, prop(value), breaks or bins, size_range or [2, 14]),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'point'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'point'),
            'filter': animation_filter
        },
        'line': {
            'color': 'opacity({0}, {1})'.format(
                get_value(color, 'color', 'line'),
                get_value(opacity, 0.8)),
            'width': 'ramp({0}({1}, {2}), {3})'.format(
                func, prop(value), breaks or bins, size_range or [1, 10]),
            'filter': animation_filter
        }
    }

    return Style(
        data,
        value,
        default_legend=size_bins_legend(title=value),
        default_widget=histogram_widget(value, title=value),
        default_popup_hover=popup_element(value, title=value),
        default_popup_click=popup_element(value, title=value)
    )
