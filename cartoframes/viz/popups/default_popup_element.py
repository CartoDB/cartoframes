def default_popup_element(title=None, operation=None):
    """Helper function for quickly adding a default popup element based on the style.
    A style helper is required.

    Args:
        title (str, optional): Title for the given value. By default, it's the name of the value.
        operation (str, optional): Cluster operation, defaults to 'count'. Other options
          available are 'avg', 'min', 'max', and 'sum'.

    Example:
        >>> default_popup_element(title='Popup title')

    """
    return {
      'value': None,
      'title': title,
      'operation': operation
    }
