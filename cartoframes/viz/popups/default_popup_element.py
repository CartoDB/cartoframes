def default_popup_element(title=None, operation=None, format=None):
    """Helper function for quickly adding a default popup element based on the style.
    A style helper is required.

    Args:
        title (str, optional): Title for the given value. By default, it's the name of the value.
        operation (str, optional): Cluster operation, defaults to 'count'. Other options
          available are 'avg', 'min', 'max', and 'sum'.
        format (str, optional): Format to apply to number values in the widget, based on d3-format
            specifier (https://github.com/d3/d3-format#locale_format).

    Example:
        >>> default_popup_element(title='Popup title', format='.2~s')

    """
    return {
      'value': None,
      'title': title,
      'operation': operation,
      'format': format
    }
