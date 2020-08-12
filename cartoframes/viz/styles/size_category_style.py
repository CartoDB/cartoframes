from ..style import Style
from ..legends import size_category_legend
from ..widgets import category_widget
from ..popups import popup_element


def size_category_style(value, top=5, cat=None, size_range=None, color=None, opacity=None,
                        stroke_color=None, stroke_width=None, animate=None):
    """Helper function for quickly creating a size category style.

    Args:
        value (str): Column to symbolize by.
        top (int, optional): Number of size categories. Default is 5. Values
            can range from 1 to 16.
        cat (list<str>, optional): Category list as a string.
        size_range (list<int>, optional): Min/max size array as a string. Default is
            [2, 20] for point geometries and [1, 10] for lines.
        color (str, optional): hex, rgb or named color value.
            Default is '#F46D43' for point geometries and '#4CC8A3' for lines.
        opacity (float, optional): Opacity value for point color and line features.
            Default is 0.8.
        stroke_color (str, optional): Color of the stroke on point features.
            Default is '#222'.
        stroke_width (int, optional): Size of the stroke on point features.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        cartoframes.viz.style.Style

    """
    if animate:
        raise NotImplementedError('`animate` parameter for `size_category_style` not implemented yet in WebSDK.')

    size_range_ = None
    if size_range and isinstance(size_range, (list, tuple)) and len(size_range) >= 2:
        size_range_ = [size_range[0], size_range[-1]]

    data = {
        'name': 'sizeCategories',
        'value': value,
        'properties': {
            'top': top,
            'cat': cat,
            'sizeRange': size_range_,
            'color': color,
            'opacity': opacity,
            'strokeColor': stroke_color,
            'strokeWidth': stroke_width,
            'animate': animate
        }
    }

    return Style(
        data,
        value,
        default_legend=size_category_legend(title=value),
        default_widget=category_widget(value, title=value),
        default_popup_hover=popup_element(value, title=value),
        default_popup_click=popup_element(value, title=value)
    )
