from .utils import get_value
from ..style import Style
from ..widgets import basic_widget


def basic_style(color=None, size=None, opacity=None, stroke_color=None, stroke_width=None):
    """Helper function for quickly creating a basic style.

    Args:
        color (str, optional): hex, rgb or named color value.
            Defaults is '#FFB927' for point geometries and '#4CC8A3' for lines.
        size (int, optional): Size of point or line features.
        opacity (float, optional): Opacity value. Default is 1 for points and lines and
            0.9 for polygons.
        stroke_color (str, optional): Color of the stroke on point features.
            Default is '#222'.
        stroke_width (int, optional): Size of the stroke on point features.

    Returns:
        cartoframes.viz.style.Style

    """
    value = None
    data = {
        'point': {
            'color': 'opacity({0}, {1})'.format(
                get_value(color, 'color', 'point'),
                get_value(opacity, 1)
            ),
            'width': get_value(size, 'width', 'point'),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'point'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'point'),
        },
        'line': {
            'color': 'opacity({0}, {1})'.format(
                get_value(color, 'color', 'line'),
                get_value(opacity, 1)
            ),
            'width': get_value(size, 'width', 'line')
        },
        'polygon': {
            'color': 'opacity({0}, {1})'.format(
                get_value(color, 'color', 'polygon'),
                get_value(opacity, 0.9)
            ),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'polygon'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'polygon')
        }
    }

    return Style(
        data,
        value,
        default_widget=basic_widget()
    )
