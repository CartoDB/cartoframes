from ..style import Style
from ..legends import size_bins_legend
from ..widgets import histogram_widget
from ..popups import popup_element


def size_bins_style(value, method='quantiles', bins=5, breaks=None, size_range=None, color=None,
                    opacity=None, stroke_color=None, stroke_width=None, animate=None):
    """Helper function for quickly creating a size bind style with
    classification method/buckets.

    Args:
        value (str): Column to symbolize by.
        method (str, optional): Classification method of data: "quantiles", "equal", "stdev".
            Default is "quantiles".
        bins (int, optional): Number of size classes (bins) for map. Default is 5.
        breaks (list<int>, optional): Assign manual class break values.
        size_range (list<int>, optional): Min/max size array as a string. Default is
            [2, 14] for point geometries and [1, 10] for lines.
        color (str, optional): Hex, rgb or named color value. Default is '#EE5D5A' for point geometries and
            '#4CC8A3' for lines.
        opacity (float, optional): Opacity value for point color and line features.
            Default is 0.8.
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
        raise NotImplementedError('`animate` parameter for `size_bins_style` not implemented yet in WebSDK.')

    size_range_ = None
    if size_range and isinstance(size_range, (list, tuple)) and len(size_range) >= 2:
        size_range_ = [size_range[0], size_range[-1]]

    data = {
        'name': 'sizeBins',
        'value': value,
        'properties': {
            'method': method,
            'bins': bins,
            'breaks': breaks,
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
        default_legend=size_bins_legend(title=value),
        default_widget=histogram_widget(value, title=value),
        default_popup_hover=popup_element(value, title=value),
        default_popup_click=popup_element(value, title=value)
    )
