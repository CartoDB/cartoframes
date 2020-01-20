from ..widget import Widget


def basic_widget(title=None, description=None, footer=None):
    """Helper function for quickly creating a default widget.

    The default widget is a general purpose widget that can be used to provide additional information about your map.

    Args:
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom.

    Returns:
        cartoframes.viz.widget.Widget

    Example:
        >>> basic_widget(
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer')

    """
    return Widget('basic', None, title, description, footer)
