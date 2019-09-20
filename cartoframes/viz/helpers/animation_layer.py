from __future__ import absolute_import

from ..layer import Layer
from .. import defaults


def animation_layer(
        source, value, title='', duration=None, fade=None, size=None,
        color=None, opacity=None, stroke_color=None, stroke_width=None,
        widget_type='time-series', description=''):
    """Helper function for quickly creating an animated map.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of widget.
        color (str, optional): Hex value, rgb expression, or other valid
          CARTO VL color. Default is '#EE5D5A' for point geometries,
          '#4CC8A3' for lines and #826DBA for polygons.
        size (int, optional): Size of point or line features.
        opacity (int, optional): Opacity value for point color and line features.
          Default is '0.8'.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
          Default is '#222'.
        widget_type (str, optional): Type of animation widget: "animation" or "time-series".
          The default is "time-series".
        description (str, optional): Description text placed under the widget title.
        fade (string, optional): Animation fade with the format: "(fade in, fade out)". Default is (1, 1).

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`. Includes Widget `value`.
    """

    return Layer(
        source,
        style={
            'point': {
                'width': '{0}'.format(
                    size or defaults.STYLE['point']['width']),
                'color': 'opacity({0}, {1})'.format(
                    color or '#EE4D5A', opacity or '0.8'),
                'strokeWidth': '{0}'.format(
                    stroke_width or defaults.STYLE['point']['strokeWidth']),
                'strokeColor': '{0}'.format(
                    stroke_color or defaults.STYLE['point']['strokeColor']),
                'filter': 'animation(linear(${0}), {1}, fade{2})'.format(
                    value, duration or 20, fade or '(1, 1)')
            },
            'line': {
                'width': '{0}'.format(
                    size or defaults.STYLE['line']['width']),
                'color': 'opacity({0}, {1})'.format(
                    color or '#4CC8A3', opacity or '0.8'),
                'filter': 'animation(linear(${0}), {1}, fade{2})'.format(
                    value, duration or 20, fade or '(1, 1)')
            },
            'polygon': {
                'color': 'opacity({0}, {1})'.format(
                    color or defaults.STYLE['polygon']['color'], opacity or '0.9'),
                'strokeColor': '{0}'.format(
                    stroke_color or defaults.STYLE['polygon']['strokeColor']),
                'strokeWidth': '{0}'.format(
                    stroke_width or defaults.STYLE['polygon']['strokeWidth']),
                'filter': 'animation(linear(${0}), {1}, fade{2})'.format(
                    value, duration or 20, fade or '(1, 1)')
            }
        },
        widgets=[{
            'type': widget_type,
            'value': value,
            'title': title,
            'description': description
        }]
    )
