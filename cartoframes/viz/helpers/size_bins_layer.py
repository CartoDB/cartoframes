from __future__ import absolute_import

from ..layer import Layer


def size_bins_layer(source, value, title='', bins=5, size=None, color=None):
    """Helper function for quickly creating a size symbol map with
    classification method/buckets.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by
        title (str, optional): Title of legend
        bins (int, optional): Number of size classes (bins) for map. Default is
          5.
        size (str, optiona): Min/max size array in CARTO VL syntax. Default is
          '[2, 14]' for point geometries and '[1, 10]' for lines.
        color (str, optional): Hex value, rgb expression, or other valid
          CARTO VL color. Default is '#EE5D5A' for point geometries and
          '#4CC8A3' for lines.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`. Includes Legend and
        popup on `value`.
    """
    return Layer(
        source,
        style={
            'point': {
                'width': 'ramp(globalQuantiles(${0}, {1}), {2})'.format(value, bins, size or [2, 14]),
                'color': 'opacity({0}, 0.8)'.format(color or '#EE4D5A')
            },
            'line': {
                'width': 'ramp(globalQuantiles(${0}, {1}), {2})'.format(value, bins, size or [1, 10]),
                'color': 'opacity({0}, 0.8)'.format(color or '#4CC8A3')
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
                'point': 'size-bins-point',
                'line': 'size-bins-line',
                'polygon': 'size-bins-polygon'
            },
            'title': title or value,
            'description': ''
        }
    )
