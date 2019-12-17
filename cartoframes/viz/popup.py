from __future__ import absolute_import

from ..utils.utils import gen_variable_name, gen_column_name


class Popup(object):
    """Popup

    Args:
        event (str): Popup type. It can be 'hover' or 'click'
        value (str): Column name to display the value for each feature
        title (str, optional): Title
    """

    def __init__(self, event=None, value=None, title=None):
        self._init_popup(event, value, title)

    def _init_popup(self, event=None, value=None, title=None):
        if event is None and value is None:
            raise ValueError('Wrong popup input')

        self._event = event
        self._value = gen_column_name(value)
        self._title = title

        self._interactivity = self._get_interactivity()
        self._variables = self._get_variables()

    def get_interactivity(self):
        return self._interactivity

    def get_variables(self):
        return self._variables

    def _get_interactivity(self):
        return {
            'event': self._event,
            'attrs': self._get_attrs()
        }

    def _get_attrs(self):
        return {
            'name': gen_variable_name(self._value),
            'title': self._title or self._value
        }

    def _get_variables(self):
        return {
            'name': gen_variable_name(self._value),
            'value': self._value
        }
