from ..style import Style
from ..helpers.utils import get_value


def animation_style(source, value, title='', duration=20, color=None,
                    size=None, opacity=None, stroke_color=None, stroke_width=None):
    """Helper function for quickly creating an animated layer
    """

    fade = '(1, 1)'

    style = {
        'point': {
            'width': get_value(size, 'point', 'width'),
            'color': 'opacity({0}, {1})'.format(color or '#EE4D5A', opacity),
            'strokeColor': get_value(stroke_color, 'point', 'strokeColor'),
            'strokeWidth': get_value(stroke_width, 'point', 'strokeWidth'),
            'filter': _animation_filter(value, duration, fade)
        },
        'line': {
            'width': get_value(size, 'line', 'width'),
            'color': 'opacity({0}, {1})'.format(color or '#4CC8A3', opacity),
            'filter': _animation_filter(value, duration, fade)
        },
        'polygon': {
            'color': get_value(color, 'polygon', 'color'),
            'strokeColor': get_value(stroke_color, 'polygon', 'strokeColor'),
            'strokeWidth': get_value(stroke_width, 'polygon', 'strokeWidth'),
            'filter': _animation_filter(value, duration, fade)
        }
    }

    return Style(style)


def _animation_filter(value, duration, fade):
    return 'animation(linear(${0}), {1}, fade{2})'.format(value, duration, fade)
