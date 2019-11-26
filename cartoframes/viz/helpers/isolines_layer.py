from __future__ import absolute_import

from . import color_category_layer
from ...data.services.isolines import RANGE_LABEL_KEY


def isolines_layer(source, value=RANGE_LABEL_KEY, **kwargs):
    """Helper function for quickly creating an isolines color map.

    Args:
        source (str, DataFrame):
        value (str, optional): Column to symbolize by. By default is "range_label".
        title (str, optional): Title of legend.
        top (int, optional): Number of category for map. Default is 11. Values
          can range from 1 to 16.
        cat (list<str>, optional): Category list. Must be a valid list of categories.
        palette (str, optional): Palette that can be a named CARTOColor palette
          or other valid CARTO VL palette expression. Default is `bold`.
        size (int, optional): Size of point or line features.
        opacity (int, optional): Opacity value for point color and line features.
          Default is '0.8'.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
          Default is '#222'.
        description (str, optional): Description text legend placed under legend title.
        footer (str, optional): Footer text placed under legend items.
        legend (bool, optional): Display map legend: "True" or "False".
          Set to "True" by default.
        popup (bool, optional): Display popups on hover and click: "True" or "False".
          Set to "True" by default.
        widget (bool, optional): Display a widget for mapped data.
          Set to "False" by default.
        animate (str, optional): Animate features by date/time or other numeric field.

    Example:

        Create a layer with a custom popup, legend, and widget.

        .. code::

            from cartoframes.viz.helpers import isolines_layer

            [...]

            data, metadata = Isolines().isodistances(df, [1200, 2400, 3600])

            isolines_layer(data, palette='purpor')

    Returns:
        :py:class:`cartoframes.viz.Layer`: Layer styled by `value`.
        Includes a legend, popup and widget on `value`.
    """

    if 'palette' not in kwargs:
        kwargs['palette'] = 'pinkyl'

    if 'stroke_color' not in kwargs:
        kwargs['stroke_color'] = 'rgba(150,150,150,0.4)'

    if 'opacity' not in kwargs:
        kwargs['opacity'] = '0.8'

    if 'title' not in kwargs:
        kwargs['title'] = 'Isolines Areas'

    return color_category_layer(source, value, **kwargs)
