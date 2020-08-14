from ..style import Style
from ..legends import color_bins_legend
from ..widgets import histogram_widget
from ..popups import popup_element


def color_bins_style(value, method='quantiles', bins=5, breaks=None, palette=None, size=None,
                     opacity=None, stroke_color=None, stroke_width=None, animate=None):
    """Helper function for quickly creating a color bins style.

    Args:
        value (str): Column to symbolize by.
        method (str, optional): Classification method of data: "quantiles", "equal", "stdev".
            Default is "quantiles".
        bins (int, optional): Number of size classes (bins) for map. Default is 5.
        breaks (list<int>, optional): Assign manual class break values.
        palette (str, optional): Palette that can be a named cartocolor palette
            or other valid color palette. Use `help(cartoframes.viz.palettes)` to
            get more information. Default is "purpor".
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
    if method not in ('quantiles', 'equal', 'stdev'):
        raise ValueError('Available methods are: "quantiles", "equal", "stdev".')

    if animate:
        raise NotImplementedError('`animate` parameter for `color_bins_style` not implemented yet in WebSDK.')

    data = {
        'name': 'colorBins',
        'value': value,
        'properties': {
            'method': method,
            'bins': bins,
            'breaks': breaks,
            'palette': palette,
            'size': size,
            'opacity': opacity,
            'strokeColor': stroke_color,
            'strokeWidth': stroke_width,
            'animate': animate
        }
    }

    return Style(
        data,
        value,
        default_legend=color_bins_legend(title=value),
        default_widget=histogram_widget(value, title=value),
        default_popup_hover=popup_element(value, title=value),
        default_popup_click=popup_element(value, title=value)
    )
