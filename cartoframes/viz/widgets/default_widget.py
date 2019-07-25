from __future__ import absolute_import

from ..widget import Widget


def default_widget(**kwargs):
    """Helper function for quickly creating a default widget.

    The default widget is a general purpose widget that can be used to provide additional information about your map.

    Args:
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom

    Returns:
        cartoframes.viz.Widget: Widget with type='default'

    Example:

        .. code::

            from cartoframes.viz import Map, Layer
            from cartoframes.viz.widgets import default_widget

            Map(
                Layer(
                    'seattle_collisions',
                    widgets=[
                        default_widget(
                            title='Road Collisions in 2018',
                            description='An analysis of collisions in Seattle, WA',
                            footer='Data source: City of Seattle'
                        )]
                )
            )
    """

    data = kwargs
    data['type'] = 'default'
    return Widget(data)
