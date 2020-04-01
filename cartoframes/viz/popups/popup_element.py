def popup_element(value, title=None):
    """Helper function for quickly adding a popup element to a layer.

    Args:
        value (str): Column name to display the value for each feature.
        title (str, optional): Title for the given value. By default, it's the name of the value.

    Example:
        >>> popup_element('column_name', title='Popup title')

    """
    return {
      'value': value,
      'title': title
    }
