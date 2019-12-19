from __future__ import absolute_import

from ..legend import Legend


def size_continuous_legend(title='', description='', footer='', prop='size',
                           variable=None, dynamic=True):
    """Helper function for quickly creating a size continuous legend

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

    Returns:
        A 'size-continuous' :py:class:`Legend <cartoframes.viz.Legend>`

    Examples:

        Default legend:

        .. code::

            from cartoframes.viz import Map, Layer, size_continuous_legend

            Map(
                Layer(
                    'seattle_collisions',
                    style=size_continuous_style('collisiontype')
                    legends=size_continuous_legend()
                )
            )

        Legend with custom parameters:

        .. code::

            from cartoframes.viz import Map, Layer, size_continuous_legend

            Map(
                Layer(
                    'seattle_collisions',
                    style=size_continuous_style('amount')
                    legends=size_continuous_legend(
                      title='Collision Type',
                      description="Seattle Collisions"
                      dynamic=False
                    )
                )
            )
    """

    return Legend('size-continuous', title, description, footer, prop, variable, dynamic)
