from .utils import get_value
from ..style import Style


def basic_style(color=None, size=None, opacity=None, stroke_color=None, stroke_width=None):
    """Helper function for quickly creating a layer with the basic style"""

    value = None
    style = {
        'point': {
            'color': get_value(color, 'color', 'point'),
            'width': get_value(size, 'width', 'point'),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'point'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'point'),
            'opacity': get_value(opacity, '1')
        },
        'line': {
            'color': get_value(color, 'color', 'line'),
            'width': get_value(size, 'width', 'line'),
            'opacity': get_value(opacity, '1')
        },
        'polygon': {
            'color': get_value(color, 'color', 'polygon'),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'polygon'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'polygon'),
            'opacity': get_value(opacity, '0.9')
        }
    }

    return Style('default', value, style)
