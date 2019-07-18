from __future__ import absolute_import

from ..layer import Layer


def size_bins_layer(
        source, value, title='', method='quantiles', bins=5,
        breaks=None, size=None, color=None, description='', footer='',
        legend=True, popup=True, widget=False, animate=None):
    """Helper function for quickly creating a size symbol map with
    classification method/buckets.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend.
        method (str, optional): Classification method of data: "quantiles", "equal", "stdev".
          Default is "quantiles".
        bins (int, optional): Number of size classes (bins) for map. Default is 5.
        breaks (int[], optional): Assign manual class break values.
        size (str, optiona): Min/max size array in CARTO VL syntax. Default is
          '[2, 14]' for point geometries and '[1, 10]' for lines.
        color (str, optional): Hex value, rgb expression, or other valid
          CARTO VL color. Default is '#EE5D5A' for point geometries and
          '#4CC8A3' for lines.
        description (str, optional): Description text legend placed under legend title.
        legend (bool, optional): Display map legend: "True" or "False".
          Set to "True" by default.
        popup (bool, optional): Display popups on hover and click: "True" or "False".
          Set to "True" by default.
        widget (bool, optional): Display a widget for mapped data.
          Set to "False" by default.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`.
        Includes a legend, popup and widget on `value`.
    """
    if method not in ('quantiles', 'equal', 'stdev'):
        raise ValueError('Available methods are: "quantiles", "equal", "stdev".')

    func = 'buckets' if breaks else {
        'quantiles': 'globalQuantiles',
        'equal': 'globalEqIntervals',
        'stdev': 'globalStandardDev'
    }.get(method)

    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'

    return Layer(
        source,
        style={
            'point': {
                'width': 'ramp({0}(${1}, {2}), {3})'.format(
                    func, value, breaks or bins, size or [2, 14]),
                'color': 'opacity({0}, 0.8)'.format(
                    color or '#EE4D5A'),
                'filter': animation_filter
            },
            'line': {
                'width': 'ramp({0}(${1}, {2}), {3})'.format(
                    func, value, breaks or bins, size or [1, 10]),
                'color': 'opacity({0}, 0.8)'.format(
                    color or '#4CC8A3'),
                'filter': animation_filter
            }
        },
        popup=popup and not animate and {
            'hover': {
                'title': title or value,
                'value': '$' + value
            }
        },
        legend=legend and {
            'type': {
                'point': 'size-bins-point',
                'line': 'size-bins-line',
                'polygon': 'size-bins-polygon'
            },
            'title': title or value,
            'description': description,
            'footer': footer
        },
        widgets=[
            animate and {
                'type': 'time-series',
                'value': animate,
                'title': 'Animation'
            },
            widget and {
                'type': 'histogram',
                'value': value,
                'title': 'Distribution'
            }
        ]
    )
