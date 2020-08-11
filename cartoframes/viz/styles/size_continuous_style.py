from ..style import Style
from ..legends import size_continuous_legend
from ..widgets import histogram_widget
from ..popups import popup_element


def size_continuous_style(value, size_range=None, range_min=None, range_max=None, color=None, opacity=None,
                          stroke_color=None, stroke_width=None, animate=None):
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
    if animate:
        raise NotImplementedError('`animate` parameter for `size_continuous_style` not implemented yet in WebSDK.')

    data = {
        'name': 'sizeContinuousStyle',
        'value': value,
        'properties': {
            'sizeRange': size_range,
            'rangeMin': range_min,
            'rangeMax': range_max,
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
        default_legend=size_continuous_legend(title=value),
        default_widget=histogram_widget(value, title=value),
        default_popup_hover=popup_element(value, title=value),
        default_popup_click=popup_element(value, title=value)
    )
