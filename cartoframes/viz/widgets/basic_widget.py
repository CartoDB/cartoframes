from ..widget import Widget


def basic_widget(title='', description='', footer=''):
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

            from cartoframes.viz import Map, Layer, basic_widget

            Map(
                Layer(
                    'seattle_collisions',
                    widgets=[
                        basic_widget(
                            title='Road Collisions in 2018',
                            description='An analysis of collisions in Seattle, WA',
                            footer='Data source: City of Seattle'
                        )]
                )
            )
    """

    return Widget('default',
                  title=title,
                  description=description,
                  footer=footer)
