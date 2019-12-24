from .utils import get_value
from ..style import Style
from ..legends import basic_legend
from ..widgets import basic_widget


def basic_style(color=None, size=None, opacity=None, stroke_color=None, stroke_width=None):
    """Helper function for quickly creating a layer with the basic style"""

    data = {
        'point': {
            'color': get_value(color, 'color', 'point'),
            'width': get_value(size, 'width', 'point'),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'point'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'point'),
            'filter': get_value(opacity, 1)
        },
        'line': {
            'color': get_value(color, 'color', 'line'),
            'width': get_value(size, 'width', 'line'),
            'filter': get_value(opacity, 1)
        },
        'polygon': {
            'color': get_value(color, 'color', 'polygon'),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'polygon'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'polygon'),
            'filter': get_value(opacity, 0.9)
        }
    }

    return Style(
        data,
        default_legends=basic_legend(),
        default_widgets=basic_widget()
    )
