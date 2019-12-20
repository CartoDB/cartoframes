def popup_element(value=None, title=None):
    """Helper function for quickly adding a popup element to a layer

    Args:
        value (str): Column name to display the value for each feature
        title (str, optional): Title for the given value. By default, it's the name of the value

    .. code::
        from cartoframes.viz import Layer, popup_element

        Layer(
            "SELECT * FROM populated_places",
            click_popup=[
                popup_element('name')
            ],
            hover_popup=[
                popup_element('name'),
                popup_element('pop_max'),
                popup_element('pop_min')
            ]
        )
    """

    return {
      'value': value,
      'title': title
    }
