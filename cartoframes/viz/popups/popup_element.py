def popup_element(value, title=None, format=None):
    """Helper function for quickly adding a popup element to a layer.

    Args:
        value (str): Column name to display the value for each feature.
        title (str, optional): Title for the given value. By default, it's the name of the value.
        format (str, optional): Format to apply to number values in the widget, based on d3-format
            specifier (https://github.com/d3/d3-format#locale_format).

    Example:
        >>> popup_element('column_name', title='Popup title', format='.2~s')

    """
    return {
        'value': value,
        'title': title,
        'format': format
    }
