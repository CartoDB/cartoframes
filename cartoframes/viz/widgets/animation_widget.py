from ..widget import Widget


def animation_widget(title=None, description=None, footer=None, format=None, prop='filter'):
    """Helper function for quickly creating an animated widget.

    The animation widget includes an animation status bar as well as controls to play or pause animated data.
    The `filter` property of your map's style, applied to either a date or numeric field, drives both
    the animation and the widget. Only **one** animation can be controlled per layer.

    Args:
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom.
        format (str, optional): Format to apply to number values in the widget, based on d3-format
            specifier (https://github.com/d3/d3-format#locale_format).
        prop (str, optional): Property of the style to get the animation. Default "filter".

    Returns:
        cartoframes.viz.widget.Widget

    Example:
        >>> animation_widget(
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer')

    """
    return Widget('animation', None, title, description, footer, format=format, prop=prop)
