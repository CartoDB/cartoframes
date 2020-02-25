from ..legend import Legend


def size_continuous_legend(title=None, description=None, footer=None, prop='size',
                           variable='size_value', dynamic=True, ascending=False):
    """Helper function for quickly creating a size continuous legend.

    Args:
        prop (str, optional): Allowed properties are 'size' and 'stroke_width'.
        dynamic (boolean, optional):
            Update and render the legend depending on viewport changes.
            Defaults to ``True``.
        title (str, optional):
            Title of legend.
        description (str, optional):
            Description in legend.
        footer (str, optional):
            Footer of legend. This is often used to attribute data sources.
        variable (str, optional):
            If the information in the legend depends on a different value than the
            information set to the style property, it is possible to set an independent
            variable.
        ascending (boolean, optional):
            If set to ``True`` the values are sorted in ascending order.
            Defaults to ``False``.

    Returns:
        cartoframes.viz.legend.Legend

    Example:
        >>> size_continuous_legend(
        ...     title='Legend title',
        ...     description='Legend description',
        ...     footer='Legend footer',
        ...     dynamic=False)

    """
    return Legend('size-continuous', title, description, footer, prop, variable, dynamic, ascending)
