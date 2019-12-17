from __future__ import absolute_import

from ..utils.utils import gen_variable_name


class Popup(object):
    """Popup

    Args:
        interactivity (str): Popup interactivity type. It can be 'hover' or 'click'
        value (str): Column name to display the value for each feature
        title (str, optional): Title
    """

    def __init__(self, interactivity=None, value=None, title=None):
        self._init_popup(interactivity, value, title)

    def _init_popup(self, interactivity=None, value=None, title=None):
        if interactivity is None and value is None:
            raise ValueError('Wrong popup input')

        self._interactivity = interactivity
        self._value = value
        self._title = title

        self._interactivity = self._get_attrs()
        self._variables = self._get_attrs()

    def get_interactivity(self):
        return self._interactivity

    def get_variables(self):
        return self._variables

    def _get_attrs(self):
        return {
            'name': gen_variable_name(self._value),
            'title': self._title or self._value
        }
