from ..legend import Legend


def basic_legend(title='', description='', footer=''):
    """Helper function for quickly creating a basic legend

    Args:
        title (str, optional):
            Title of legend.
        description (str, optional):
            Description in legend.
        footer (str, optional):
            Footer of legend. This is often used to attribute data sources

    Returns:
        :py:class:`Legend <cartoframes.viz.Legend>`

    Example:

        .. code::

            from cartoframes.viz import Map, Layer, color_bins_legend

            Map(
                Layer(
                    'seattle_collisions',
                    style=color_bins_style('amount')
                    legends=basic_legend(
                      title='Seattle Collisions',
                      description='Car accidents in the city of Seattle'
                    )
                )
            )
    """

    return Legend('default', title, description, footer)
