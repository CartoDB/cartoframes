from __future__ import absolute_import

from ..widget import Widget


def category_widget(value, **kwargs):
    """Helper function for quickly creating a category widget.

    Args:
        value (str): Column name of the category value
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom
        read_only (boolean, optional): Interactively filter a category by selecting it in the widget.
          Set to "False" by default.

    Returns:
        cartoframes.viz.Widget: Widget with type='category'

    Example:

        .. code::

            from cartoframes.viz import Map, Layer
            from cartoframes.viz.widgets import category_widget

            Map(
                Layer(
                    'seattle_collisions',
                    widgets=[
                        category_widget(
                            'collisiontype',
                            title='Type of Collision',
                            description='Select a category to filter',
                        )
                    ]
                )
            )
    """

    data = kwargs
    data['type'] = 'category'
    data['value'] = value
    data['read_only'] = kwargs.get('read_only', False)
    return Widget(data)
