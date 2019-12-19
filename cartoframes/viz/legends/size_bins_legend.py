from __future__ import absolute_import

from ..legend import Legend


def size_bins_legend(**kwargs):
    """Helper function for quickly creating a size bins legend

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

    data = kwargs
    data['type'] = 'size-bins'
    data['prop'] = data.get('prop') if data.get('prop') else 'size'

    return Legend(data)
