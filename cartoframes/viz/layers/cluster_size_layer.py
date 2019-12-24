from ..layer import Layer
from ..styles import cluster_size_style


def cluster_size_layer(
        source, value=None, operation='count', resolution=32,
        title='', color=None, opacity=None,
        stroke_width=None, stroke_color=None, description='',
        footer='', legend=True, popups=True, widget=False, animate=None, credentials=None):
    """Helper function for quickly creating a cluster map with
    continuously sized points.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Numeric column to aggregate.
        operation (str, optional): Cluster operation, defaults to 'count'. Other options
          available are 'avg', 'min', 'max', and 'sum'.
        resolution (int, optional): Resolution of aggregation grid cell. Set to 32 by default.
        title (str, optional): Title of legend and hover.
        color (str, optional): Hex, rgb or named color value. Defaults is '#FFB927' for point geometries.
        opacity (int, optional): Opacity value for point color and line features.
          Default is '0.8'.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
          Default is '#222'.
        description (str, optional): Description text legend placed under legend title.
        footer (str, optional): Footer text placed under legend items.
        legend (bool, optional): Display map legend: "True" or "False".
          Set to "True" by default.
        popups (bool, list of :py:class:`Popup <cartoframes.viz.Popup>`, default False, optional):
          Display popups on hover and click: "True" or "False". Set to "True" by default.
        widget (bool, optional): Display a widget for mapped data.
          Set to "False" by default.
        animate (str, optional): Animate features by date/time or other numeric field.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
          A Credentials instance. This is only used for the simplified Source API.
          When a :py:class:`Source <cartoframes.viz.Source>` is passed as source,
          these credentials is simply ignored. If not provided the credentials will be
          automatically obtained from the default credentials.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`.
        Includes a legend, popup and widget on `value`.
    """

    return Layer(
        source,
        style=cluster_size_style(
            value, operation, resolution, color, opacity, stroke_color, stroke_width),
        legend=legend and {
            'type': {
                'point': 'size-continuous-point'
            },
            'title': title,
            'description': description,
            'footer': footer
        },
        widgets=[
            animate and {
                'type': 'time-series',
                'value': animate,
                'title': 'Animation'
            },
            widget and value is not None and {
                'type': 'histogram',
                'value': value,
                'title': 'Distribution'
            }
        ],
        credentials=credentials
    )
