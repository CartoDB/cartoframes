from ..widget import Widget


def time_series_widget(value, title=None, description=None, footer=None, read_only=False,
                       buckets=20, prop='filter', weight=1):
    """Helper function for quickly creating a time series widget.

    The time series widget enables you to display animated data (by aggregation) over a specified date or numeric field.
    Time series widgets provide a status bar of the animation, controls to play or pause, and the ability to filter on
    a range of values.

    Args:
        value (str): Column name of the numeric or date value.
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom
        read_only (boolean, optional): Interactively filter a range of numeric values by selecting them in the widget.
          Set to "False" by default.
        buckets (number, optional): Number of histogram buckets. Set to 20 by default.

    Returns:
        cartoframes.viz.widget.Widget

    Example:
        >>> time_series_widget(
        ...     'column_name',
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer',
        ...     buckets=10)

    """
    return Widget('time-series', value, title, description, footer,
                  read_only=read_only, buckets=buckets, prop=prop, weight=weight)
