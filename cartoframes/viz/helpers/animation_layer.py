from __future__ import absolute_import

from ..layer import Layer


def animation_layer(
        source, value, title='', color=None, widget_type='time-series', description=''):
    """Helper function for quickly creating an animated map.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend.
        color (str, optional): Hex value, rgb expression, or other valid
          CARTO VL color. Default is '#EE5D5A' for point geometries,
          '#4CC8A3' for lines and 'TODO' for polygons.
        widget_type (str, optional): Type of animation widget: "animation" or "time-series".
          The default is "time-series".
        description (str, optional): Description text legend placed under legend title.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`. Includes Widget `value`.
    """
    return Layer(
        source,
        style={
            'point': {
                'color': 'opacity({0}, 0.8)'.format(color or '#EE4D5A'),
                'filter': 'animation(linear(${0}), 20, fade(1,1))'.format(value)
            },
            'line': {
                'color': 'opacity({0}, 0.8)'.format(color or '#4CC8A3'),
                'filter': 'animation(linear(${0}), 20, fade(1,1))'.format(value)
            },
            'polygon': {
                'color': 'opacity({0}, 0.8)'.format(color or 'TODO'),
                'filter': 'animation(linear(${0}), 20, fade(1,1))'.format(value)
            }
        },
        widgets=[{
            'type': widget_type,
            'value': value,
            'title': title,
            'description': description
        }]
    )
