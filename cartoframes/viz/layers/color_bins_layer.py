from ..legends.color_bins_legend import color_bins_legend
from ..widgets.time_series_widget import time_series_widget
from ..widgets.histogram_widget import histogram_widget
from ..layer import Layer
from ..styles import color_bins_style


def color_bins_layer(
        source, value, title='', method='quantiles', bins=5,
        breaks=None, palette=None, size=None, opacity=None,
        stroke_color=None, stroke_width=None, description='',
        footer='', legends=True, popups=True, widgets=False, animate=None, credentials=None):
    """Helper function for quickly creating a classed color map.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend.
        method (str, optional): Classification method of data: "quantiles", "equal", "stdev".
          Default is "quantiles".
        bins (int, optional): Number of size classes (bins) for map. Default is 5.
        breaks (list<int>, optional): Assign manual class break values.
        palette (str, optional): Palette that can be a named cartocolor palette
          or other valid color palette. Use `help(cartoframes.viz.color_palettes)` to
          get more information. Default is "purpor".
        size (int, optional): Size of point or line features.
        opacity (int, optional): Opacity value for point color and line features.
          Default is '0.8'.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
          Default is '#222'.
        description (str, optional): Description text legend placed under legend title.
        footer (str, optional): Footer text placed under legend items.
        legends (bool, optional): Display map legend: "True" or "False".
          Set to "True" by default.
        popups (bool, list of :py:class:`Popup <cartoframes.viz.Popup>`, optional):
          Display popups on hover and click: "True" or "False". Set to "True" by default.
        widgets (bool, optional): Display a widget for mapped data: "True" or "False".
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

    default_legends = [
        color_bins_legend(title=title or value, description=description, footer=footer)
    ]

    default_widgets = [
        time_series_widget(animate, title='Animation'),
        histogram_widget(value, title='Distribution')
    ]

    return Layer(
        source,
        style=color_bins_style(
          value, method, bins, breaks, palette, size, opacity, stroke_color, stroke_width, animate),
        legends=legends and default_legends,
        widgets=widgets and default_widgets,
        credentials=credentials
    )
