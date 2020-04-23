from ..widget import Widget


def category_widget(value, title=None, description=None, footer=None, read_only=False, weight=1, format_number=None):
    """Helper function for quickly creating a category widget.

    Args:
        value (str): Column name of the category value.
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom.
        read_only (boolean, optional): Interactively filter a category by selecting it in the widget.
          Set to "False" by default.
        format_number (str, optional): Format to apply to number values in the widget, based on
          d3-format specifier (https://github.com/d3/d3-format#locale_format).

    Returns:
        cartoframes.viz.widget.Widget

    Example:
        >>> category_widget(
        ...     'column_name',
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer',
        ...     format_number='.2~s')

    """
    return Widget('category', value, title, description, footer,
                  read_only=read_only, weight=weight, format_number=format_number)
