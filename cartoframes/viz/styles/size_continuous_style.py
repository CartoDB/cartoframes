from .utils import get_value, prop
from ..style import Style
from ..legends import size_continuous_legend
from ..widgets import histogram_widget
from ..popups import popup_element


def size_continuous_style(value, size_range=None, range_min=None, range_max=None, color=None, opacity=None,
                          stroke_color=None, stroke_width=None, animate=None, credentials=None):
    """Helper function for quickly creating a size continuous style.

    Args:
        value (str): Column to symbolize by.
        size_range (list<int>, optional): Min/max size array as a string. Default is
            [2, 40] for point geometries and [1, 10] for lines.
        range_min (int, optional): The minimum value of the data range for the continuous
            size ramp. Defaults to the globalMIN of the dataset.
        range_max (int, optional): The maximum value of the data range for the continuous
            size ramp. Defaults to the globalMAX of the dataset.
        color (str, optional): hex, rgb or named color value.
            Defaults is '#FFB927' for point geometries and '#4CC8A3' for lines.
        opacity (float, optional): Opacity value for point color and line features.
            Default is 0.8.
        stroke_color (str, optional): Color of the stroke on point features.
            Default is '#222'.
        stroke_width (int, optional): Size of the stroke on point features.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        cartoframes.viz.style.Style

    """
    animation_filter = 'animation(linear({}), 20, fade(1,1))'.format(prop(animate)) if animate else '1'

    if range_min is None:
        range_min = 'globalMIN({0})'.format(prop(value))

    if range_max is None:
        range_max = 'globalMAX({0})'.format(prop(value))

    data = {
        'point': {
            '@size_value': 'ramp(linear({0}, {1}, {2}), {3})'.format(
                prop(value), range_min, range_max, size_range or [2, 40]),
            'color': 'opacity({0}, {1})'.format(
                get_value(color, '#FFB927'),
                get_value(opacity, 0.8)),
            'width': 'ramp(linear(sqrt({0}), sqrt({1}), sqrt({2})), {3})'.format(
                prop(value), range_min, range_max, size_range or [2, 40]),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'point'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'point'),
            'filter': animation_filter
        },
        'line': {
            '@size_value': 'ramp(linear({0}, {1}, {2}), {3})'.format(
                prop(value), range_min, range_max, size_range or [1, 10]),
            'color': 'opacity({0}, {1})'.format(
                get_value(color, 'color', 'line'),
                get_value(opacity, 0.8)),
            'width': 'ramp(linear({0}, {1}, {2}), {3})'.format(
                prop(value), range_min, range_max, size_range or [1, 10]),
            'filter': animation_filter
        }
    }

    return Style(
        data,
        value,
        default_legend=size_continuous_legend(title=value),
        default_widget=histogram_widget(value, title=value),
        default_popup_hover=popup_element(value, title=value),
        default_popup_click=popup_element(value, title=value)
    )
