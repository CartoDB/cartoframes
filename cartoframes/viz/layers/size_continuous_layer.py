from ..layer import Layer
from ..styles import size_continuous_style


def size_continuous_layer(
        source, value, title='', range_min=None, range_max=None, size=None, color=None,
        opacity=None, stroke_width=None, stroke_color=None, description='', footer='',
        legend=True, popups=True, widget=False, animate=None, credentials=None):
    """Helper function for quickly creating a size symbol map with
    continuous size scaled by `value`.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend and popup hover.
        color (str, optional): Hex, rgb or named color value. Defaults is '#FFB927' for point geometries and
          '#4CC8A3' for lines.
        size (str, optional): Min/max size array as a string. Default is
          '[2, 40]' for point geometries and '[1, 10]' for lines.
        range_min (int, optional): The minimum value of the data range for the continuous
          size ramp. Defaults to the globalMIN of the dataset.
        range_max (int, optional): The maximum value of the data range for the continuous
          size ramp. Defaults to the globalMAX of the dataset.
        opacity (float, optional): Opacity value for point color and line features.
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
        style=size_continuous_style(
          value, range_min, range_max, size, color, opacity, stroke_color, stroke_width, animate),
        legend=legend and {
            'type': {
                'point': 'size-continuous-point',
                'line': 'size-continuous-line',
                'polygon': 'size-continuous-polygon'
            },
            'variable': 'width_value',
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
        ],
        credentials=credentials
    )
