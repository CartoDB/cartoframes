from ..layer import Layer
from ..styles import animation_style


def animation_layer(
        source, value, title='', duration=None, fade=None, size=None,
        color=None, opacity=None, stroke_color=None, stroke_width=None,
        widget_type='time-series', description='', credentials=None):
    """Helper function for quickly creating an animated map.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of widget.
        color (str, optional): Hex, rgb or named color value. Default is '#EE5D5A' for point geometries,
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
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
          A Credentials instance. This is only used for the simplified Source API.
          When a :py:class:`Source <cartoframes.viz.Source>` is passed as source,
          these credentials is simply ignored. If not provided the credentials will be
          automatically obtained from the default credentials.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`. Includes Widget `value`.

    """
    return Layer(
        source,
        style=animation_style(
          value, duration, color, size, opacity, stroke_color, stroke_width),
        widgets=[{
            'type': widget_type,
            'value': value,
            'title': title,
            'description': description
        }],
        credentials=credentials
    )
