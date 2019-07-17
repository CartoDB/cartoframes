from __future__ import absolute_import

from ..layer import Layer


def animation_layer(
        source, value, title='', widget='animation', description=''):
    """Helper function for quickly creating an animated map

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend.
        widget (str, optional): Type of animation widget: "animation" or "time-series".
          The default is "animation".
        description (str, optional): Description text legend placed under legend title.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`. Includes Widget `value`.
    """
    return Layer(
        source,
        style={
            'filter': 'animation(linear(${0}), 20, fade(1,1))'.format(value)
        },
        widgets=[{
            'type': widget,
            'value': value,
            'title': title,
            'description': description
        }]
    )
