from __future__ import absolute_import

from ..popup import Popup


def hover_popup(value=None, title=None, operation=False):
    """Helper function for quickly creating a :py:class:`Popup <cartoframes.viz.Popup>` for hover events.

    Args:
        value (str): Column name to display the value for each feature
        title (str, optional): Title for the given value. By default, it's the name of the value

    Example:

    .. code::

        from cartoframes.viz import Map, Layer, hover_popup

        Map(
            Layer(
                'buildings_table',
                popups=[
                    hover_popup('amount')
                ]
            )
        )

    .. code::

        from cartoframes.viz import Map, Layer, hover_popup

        Map(
            Layer(
                'buildings_table',
                popups=[
                    hover_popup('amount', title='Price $')
                ]
            )
        )
    """

    return Popup('hover', value, title, operation)
