from __future__ import absolute_import

from ..utils import gen_variable_name


class Popup(object):
    """Popup

    Args:
        

    Example:

    """

    def __init__(self, data=None):
        self._click = []
        self._hover = []

        if data is not None:
            if isinstance(data, dict):
                # TODO: error control

                if 'click' in data:
                    self._click = data.get('click', [])

                if 'hover' in data:
                    self._hover = data.get('hover', [])

            else:
                raise ValueError('Wrong popup input')

    def get_interactivity(self):
        click_vars = {}
        hover_vars = {}

        self._get_vars(click_vars, self._click)
        self._get_vars(hover_vars, self._hover)

        interactivity = []

        if len(self._click) > 0:
            interactivity.append({
                'event': 'click',
                'values': click_vars
            })

        if len(self._hover) > 0:
            interactivity.append({
                'event': 'hover',
                'values': hover_vars
            })

        return interactivity

    def get_variables(self):
        variables = {}
        self._get_vars(variables, self._click)
        self._get_vars(variables, self._hover)
        return variables

    def _get_vars(self, output, array):
        for value in array:
            name = gen_variable_name(value)
            output[name] = value
