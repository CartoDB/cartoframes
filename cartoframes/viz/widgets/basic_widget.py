from ..widget import Widget


def basic_widget(title=None, description=None, footer=None, format=None):
    """Helper function for quickly creating a default widget.

    The default widget is a general purpose widget that can be used to provide additional information about your map.

    Args:
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom.
        format (str, optional): Format to apply to number values in the widget, based on d3-format
            specifier (https://github.com/d3/d3-format#locale_format).

    Returns:
        cartoframes.viz.widget.Widget

    Example:
        >>> basic_widget(
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer')

    """
    return Widget('basic', None, title, description, footer, format=format)
