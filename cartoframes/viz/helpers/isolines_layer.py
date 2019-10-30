from __future__ import absolute_import

from pandas import DataFrame

from . import color_category_layer
from ...data.dataset.dataset import Dataset


def isolines_layer(source, value='data_range', **kwargs):
    """Helper function for quickly creating an isolines color map.

    Args:
        source (:py:class:`cartoframes.data.Dataset>`, DataFrame or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by. By default is "data_range".
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

            isodistances = Isolines().isodistances(df, [1200, 2400, 3600], exclusive=True)

            isolines_layer(isodistances, palette='purpor')

    Returns:
        :py:class:`cartoframes.viz.Layer`: Layer styled by `value`.
        Includes a legend, popup and widget on `value`.
    """

    if isinstance(source, DataFrame):
        df = source
    elif isinstance(source, Dataset):
        df = source.dataframe
    elif isinstance(source, tuple) and hasattr(source, 'data'):
        df = source.data
    else:
        raise ValueError('Invalid input source. It must be a DataFrame, Dataset or a namedtuple with data.')

    df = df.copy()
    if value not in df:
        raise ValueError('Input DataFrame source must contain a "{}" column'.format(value))

    RANGE_LABEL_KEY = 'range_label'
    df[RANGE_LABEL_KEY] = df.apply(
        lambda r: '%.0f min.' % (r[value]/60), axis=1)

    if 'palette' not in kwargs:
        kwargs['palette'] = 'pinkyl'

    if 'stroke_color' not in kwargs:
        kwargs['stroke_color'] = 'rgba(150,150,150,0.4)'

    if 'opacity' not in kwargs:
        kwargs['opacity'] = '0.8'

    if 'title' not in kwargs:
        kwargs['title'] = 'Isolines Areas'

    return color_category_layer(df, RANGE_LABEL_KEY, **kwargs)
