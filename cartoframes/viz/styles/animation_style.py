from .utils import get_value, prop
from ..style import Style
from ..widgets import time_series_widget
from ..popups import popup_element


def animation_style(value, duration=20, fade_in=1, fade_out=1, color=None,
                    size=None, opacity=None, stroke_color=None, stroke_width=None):
    """Helper function for quickly creating an animated style.

    Args:
        value (str): Column to symbolize by.
        duration (float, optional): Time of the animation in seconds. Default is 20s.
        fade_in (float, optional): Time of fade in transitions in seconds. Default is 1s.
        fade_out (float, optional): Time of fade out transitions in seconds. Default is 1s.
        color (str, optional): Hex, rgb or named color value. Default is '#EE5D5A' for points,
            '#4CC8A3' for lines and #826DBA for polygons.
        size (int, optional): Size of point or line features.
        opacity (float, optional): Opacity value. Default is 1 for points and lines and
            0.9 for polygons.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
            Default is '#222'.

    Returns:
        cartoframes.viz.style.Style

    """
    fade = '({0}, {1})'.format(fade_in, fade_out)
    data = {
        'point': {
            'color': 'opacity({0}, {1})'.format(
                get_value(color, 'color', 'point'),
                get_value(opacity, 1)),
            'width': get_value(size, 'width', 'point'),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'point'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'point'),
            'filter': _animation_filter(value, duration, fade)
        },
        'line': {
            'color': 'opacity({0}, {1})'.format(
                get_value(color, 'color', 'line'),
                get_value(opacity, 1)),
            'width': get_value(size, 'width', 'line'),
            'filter': _animation_filter(value, duration, fade)
        },
        'polygon': {
            'color': 'opacity({0}, {1})'.format(
                get_value(color, 'color', 'polygon'),
                get_value(opacity, 0.9)),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'polygon'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'polygon'),
            'filter': _animation_filter(value, duration, fade)
        }
    }

    return Style(
        data,
        value,
        default_widget=time_series_widget(value, title=value),
        default_popup_hover=popup_element(value, title=value),
        default_popup_click=popup_element(value, title=value)
    )


def _animation_filter(value, duration, fade):
    return 'animation(linear({0}), {1}, fade{2})'.format(prop(value), duration, fade)
