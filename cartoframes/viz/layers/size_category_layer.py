from ..layer import Layer
from ..styles import size_category_style
from ..styles.utils import get_popup


def size_category_layer(
        source, value, title='', top=5, cat=None,
        ranges=None, color=None, opacity=None, stroke_width=None,
        stroke_color=None, description='', footer='',
        legend=True, popups=True, widget=False, animate=None, credentials=None):
    """Helper function for quickly creating a size category layer.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend.
        top (int, optional): Number of size categories for layer. Default is
          5. Valid values range from 1 to 16.
        cat (str, optional): Category list as a string.
        ranges (str, optional): Min/max size array. Default is
          '[2, 20]' for point geometries and '[1, 10]' for lines.
        color (str, optional): Hex, rgb or named color value. Default is '#F46D43' for point geometries and
          '#4CC8A3' for lines.
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
        style=size_category_style(
          value, top, cat, ranges, color, opacity, stroke_color, stroke_width, animate),
        popups=popups and not animate and get_popup(
          popups, title, value, value),
        legend=legend and {
            'type': {
                'point': 'size-category-point',
                'line': 'size-category-line',
                'polygon': 'size-category-polygon'
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
                'type': 'category',
                'value': value,
                'title': 'Categories'
            }
        ],
        credentials=credentials
    )
