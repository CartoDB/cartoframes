from ..legend import Legend


def size_bins_legend(title='', description='', footer='', prop='size',
                     variable=None, dynamic=True):
    """Helper function for quickly creating a size bins legend

    Args:
        title (str, optional):
            Title of legend.
        description (str, optional):
            Description in legend.
        footer (str, optional):
            Footer of legend. This is often used to attribute data sources.
        prop (str, optional): Allowed properties are 'size' and 'stroke-width'.
            It is 'size' by default.
        variable (str, optional):
            If the information in the legend depends on a different value than the
            information set to the style property, it is possible to set an independent
            variable.
        dynamic (boolean, optional):
            Update and render the legend depending on viewport changes.
            Defaults to ``True``.

    Returns:
        A 'size-bins' :py:class:`Legend <cartoframes.viz.Legend>`

    Examples:

        Default legend:

        .. code::

            from cartoframes.viz import Map, Layer, size_bins_legend

            Map(
                Layer(
                    'seattle_collisions',
                    style=size_bins_style('amount')
                    legends=size_bins_legend()
                )
            )

        Legend with custom parameters:

        .. code::

            from cartoframes.viz import Map, Layer, size_bins_legend

            Map(
                Layer(
                    'seattle_collisions',
                    style=size_bins_style('amount')
                    legends=size_bins_legend(
                      title='Collision Type',
                      description="Seattle Collisions"
                      dynamic=False
                    )
                )
            )
    """

    return Legend('size-bins', title, description, footer, prop, variable, dynamic)
