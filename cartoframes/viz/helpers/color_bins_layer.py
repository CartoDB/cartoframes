from __future__ import absolute_import

from ..layer import Layer


def color_bins_layer(
        source, value, title='', method='quantiles', bins=5,
        breaks=None, palette=None, description='', footer=''):
    """Helper function for quickly creating a classed color map

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend.
        method (str, optional): Classification method of data: "quantiles", "equal", "stdev". 
          Default is "quantiles".
        bins (int, optional): Number of size classes (bins) for map. Default is 5.
        breaks (int[], optional): Assign manual class break values.
        palette (str, optional): Palette that can be a named cartocolor palette
          or other valid CARTO VL palette expression. Default is `purpor`.
        description (str, optional): Description text legend placed under legend title.
        footer (str, optional): Footer text placed under legend items.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`. Includes Legend and
        popup on `value`.
    """
    if method not in ('quantiles', 'equal', 'stdev'):
        raise ValueError('Available methods are: "quantiles", "equal", "stdev".')

    func = 'buckets' if breaks else {
        'quantiles': 'globalQuantiles',
        'equal': 'globalEqIntervals',
        'stdev': 'globalStandardDev'
    }.get(method)

    default_palette = 'purpor' if breaks else {
        'quantiles': 'purpor',
        'equal': 'purpor',
        'stdev': 'temps'
    }.get(method)

    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp({0}(${1}, {2}), {3})'.format(
                    func, value, breaks or bins, palette or default_palette)
            },
            'line': {
                'color': 'ramp({0}(${1}, {2}), {3})'.format(
                    func, value, breaks or bins, palette or default_palette)
            },
            'polygon': {
                'color': 'opacity(ramp({0}(${1}, {2}), {3}), 0.9)'.format(
                    func, value, breaks or bins, palette or default_palette)
            }
        },
        popup={
            'hover': {
                'title': title or value,
                'value': '$' + value
            }
        },
        legend={
            'type': {
                'point': 'color-bins-point',
                'line': 'color-bins-line',
                'polygon': 'color-bins-polygon'
            },
            'title': title or value,
            'description': description,
            'footer': footer
        }
    )
