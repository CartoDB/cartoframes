from __future__ import absolute_import

from ..utils.utils import gen_variable_name, gen_column_name


class Popup(object):
    """Popup

    Args:
        event (str): Popup type. It can be 'hover' or 'click'
        value (str): Column name to display the value for each feature
        title (str, optional): Title for the given value. By default, it's the name of the value

    Example:

    .. code::

        from cartoframes.viz import Map, Layer, Popup

        Map(
            Layer(
                'buildings_table',
                popups=Popup('hover', value='amount')
            )
        )

    .. code::

        from cartoframes.viz import Map, Layer, Popup

        Map(
            Layer(
                'buildings_table',
                popups=[
                    Popup('click', value='amount', title='Price $')
                ]
            )
        )
    """

    def __init__(self, event=None, value=None, title=None, operation=False):
        self._init_popup(event, value, title, operation)

    def _init_popup(self, event=None, value=None, title=None, operation=False):
        if not isinstance(event, str) and not isinstance(value, str):
            raise ValueError('Wrong popup input')

        self._event = event
        self._value = gen_column_name(value, operation)
        self._title = title if title else value

        self._interactivity = self._get_interactivity()
        self._variable = self._get_variable()

    @property
    def value(self):
        return self._value

    @property
    def title(self):
        return self._title

    @property
    def interactivity(self):
        return self._interactivity

    @property
    def variable(self):
        return self._variable

    def _get_interactivity(self):
        return {
            'event': self._event,
            'attrs': self._get_attrs()
        }

    def _get_attrs(self):
        return {
            'name': gen_variable_name(self._value),
            'title': self._title
        }

    def _get_variable(self):
        return {
            'name': gen_variable_name(self._value),
            'value': self._value
        }
