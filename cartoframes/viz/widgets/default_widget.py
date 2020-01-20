from ..widget import Widget


def default_widget(title=None, description=None, footer=None, **kwargs):
    """Helper function for quickly creating a default widget based on the style.
    A style helper is required.

    Args:
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom.

    Returns:
        cartoframes.viz.widget.Widget

    Example:
        >>> default_widget(
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer')

    """
    return Widget('default', None, title=title, description=description, footer=footer, **kwargs)
