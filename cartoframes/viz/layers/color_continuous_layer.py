from ..layer import Layer
from ..styles import color_continuous_style


def color_continuous_layer(
        source, value, title='', range_min=None, range_max=None,
        palette=None, size=None, opacity=None, stroke_color=None,
        stroke_width=None, description='', footer='', legend=True, popups=True,
        widget=False, animate=None, credentials=None):
    """Helper function for quickly creating a continuous color map.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
            or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend and popup hover.
        range_min (int, optional): The minimum value of the data range for the continuous
            color ramp. Defaults to the globalMIN of the dataset.
        range_max (int, optional): The maximum value of the data range for the continuous
            color ramp. Defaults to the globalMAX of the dataset.
        palette (str, optional): Palette that can be a named cartocolor palette
            or other valid color palette. Use `help(cartoframes.viz.palettes)` to
            get more information. Default is "bluyl".
        size (int, optional): Size of point or line features.
        opacity (int, optional): Opacity value for point color and line features.
            Default is 0.8.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
            Default is '#222'.
        description (str, optional): Description text legend placed under legend title.
        footer (str, optional): Footer text placed under legend items.
        legend (bool, optional): Display map legend: "True" or "False".
            Set to "True" by default.
        popups (bool, Popup, optional): Display popups on hover and click: "True" or "False".
            Set to "True" by default.
        widget (bool, optional): Display a widget for mapped data.
            Set to "False" by default.
        animate (str, optional): Animate features by date/time or other numeric field.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            A Credentials instance. This is only used for the simplified Source API.
            When a :py:class:`Source <cartoframes.viz.Source>` is passed as source,
            these credentials is simply ignored. If not provided the credentials will be
            automatically obtained from the default credentials.


    Returns:
        cartoframes.viz.Layer

    """
    return Layer(
        source,
        style=color_continuous_style(
          value, range_min, range_max, palette, size, opacity, stroke_color, stroke_width),
        legend=legend and {
            'type': {
                'point': 'color-continuous-point',
                'line': 'color-continuous-line',
                'polygon': 'color-continuous-polygon'
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
        ],
        credentials=credentials
    )
