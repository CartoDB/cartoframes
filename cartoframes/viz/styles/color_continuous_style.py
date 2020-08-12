from ..style import Style
from ..legends import color_continuous_legend
from ..widgets import histogram_widget
from ..popups import popup_element


def color_continuous_style(value, size=None, range_min=None, range_max=None, palette=None, opacity=None,
                           stroke_color=None, stroke_width=None, animate=None):
    """Helper function for quickly creating a color continuous style.

    Args:
        value (str): Column to symbolize by.
        range_min (int, optional): The minimum value of the data range for the continuous
            color ramp. Defaults to the globalMIN of the dataset.
        range_max (int, optional): The maximum value of the data range for the continuous
            color ramp. Defaults to the globalMAX of the dataset.
        palette (str, optional): Palette that can be a named cartocolor palette
            or other valid color palette. Use `help(cartoframes.viz.palettes)` to
            get more information. Default is "bluyl".
        size (int, optional): Size of point or line features.
        opacity (float, optional): Opacity value. Default is 1 for points and lines and
            0.9 for polygons.
        stroke_color (str, optional): Color of the stroke on point features.
            Default is '#222'.
        stroke_width (int, optional): Size of the stroke on point features.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        cartoframes.viz.style.Style

    """
    if animate:
        raise NotImplementedError('`animate` parameter for `color_continuous_style` not implemented yet in WebSDK.')

    data = {
        'name': 'colorContinuous',
        'value': value,
        'properties': {
            'size': size,
            'rangeMin': range_min,
            'rangeMax': range_max,
            'palette': palette,
            'opacity': opacity,
            'strokeColor': stroke_color,
            'strokeWidth': stroke_width,
            'animate': animate
        }
    }

    return Style(
        data,
        value,
        default_legend=color_continuous_legend(title=value),
        default_widget=histogram_widget(value, title='Distribution'),
        default_popup_hover=popup_element(value, title=value),
        default_popup_click=popup_element(value, title=value)
    )
