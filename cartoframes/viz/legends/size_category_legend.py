from __future__ import absolute_import

from ..legend import Legend


def size_category_legend(**kwargs):
    """Helper function for quickly creating a size category legend

    Args:
        prop (str, optional): Allowed properties are 'size' and 'stroke_width'.
            It is 'size' by default.
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
        A 'size-category' :py:class:`Legend <cartoframes.viz.Legend>`

    Examples:

        Default legend:

        .. code::

            from cartoframes.viz import Map, Layer, size_category_legend

            Map(
                Layer(
                    'seattle_collisions',
                    style=size_category_style('collisiontype')
                    legends=size_category_legend()
                )
            )

        Legend with custom parameters:

        .. code::

            from cartoframes.viz import Map, Layer, size_category_legend

            Map(
                Layer(
                    'seattle_collisions',
                    style=size_category_style('collisiontype')
                    legends=size_category_legend(
                      title='Collision Type',
                      description="Seattle Collisions"
                      dynamic=False
                    )
                )
            )
    """

    data = kwargs
    data['type'] = 'size-category'
    data['prop'] = data.get('prop') if data.get('prop') else 'size'

    return Legend(data)
