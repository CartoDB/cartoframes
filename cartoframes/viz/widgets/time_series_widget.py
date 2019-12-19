from __future__ import absolute_import

from ..widget import Widget


def time_series_widget(value, title='', description='', footer='', read_only=False, buckets=20):
    """Helper function for quickly creating a time series widget.

    The time series widget enables you to display animated data (by aggregation) over a specified date or numeric field.
    Time series widgets provide a status bar of the animation, controls to play or pause, and the ability to filter on
    a range of values.

    Args:
        value (str): Column name of the numeric or date value
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom
        buckets (number, optional): Number of histogram buckets. Set to 20 by default.
        read_only (boolean, optional): Interactively filter a range of numeric values by selecting them in the widget.
          Set to "False" by default.

    Returns:
        cartoframes.viz.Widget: Widget with type='time-series'

    Example:

        .. code::

            from cartoframes.viz import Map, Layer, time_series_widget

            Map(
                Layer(
                    'seattle_collisions',
                    'filter: animation($incdate, 20, fade(0.5,0.5))',
                    widgets=[
                        time_series_widget(
                            value='incdate',
                            title='Number of Collisions by Date',
                            description= 'Play, pause, or select a range for the animation',
                            buckets=10
                        )]
                )
            )
    """

    return Widget('time-series',
                  value=value,
                  title=title,
                  description=description,
                  footer=footer,
                  read_only=read_only,
                  buckets=buckets)
