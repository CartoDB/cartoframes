def popup_element(value=None, title=None, operation=None):
    """Helper function for quickly adding a popup element to a layer.

    Args:
        value (str): Column name to display the value for each feature.
        title (str, optional): Title for the given value. By default, it's the name of the value.
        operation (str, optional): Cluster operation, defaults to 'count'. Other options
          available are 'avg', 'min', 'max', and 'sum'.

    Example:
        >>> popup_element('column_name', title='Popup title')

    """
    return {
      'value': value,
      'title': title,
      'operation': operation
    }
