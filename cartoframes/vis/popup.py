from __future__ import absolute_import

import hashlib


class Popup(object):
    """Popup

    Args:
        

    Example:

    """

    def __init__(self, data=None):
        self._click = [
            'sqrt($pop_max)'
        ]
        self._hover = [
            '$pop_max'
        ]

        # if isinstance(data, dict):
        #     # TODO: error control

        #     if 'click' in data:
        #         self.click = data.get('click', [])

        #     if 'hover' in data:
        #         self.hover = data.get('hover', [])

        # else:
        #     raise ValueError('Wrong popup input')

    def get_interactivity(self):
        click_vars = []
        hover_vars = []

        for value in self._click:
            click_vars.append(_gen_variable_name(value))
    
        for value in self._hover:
            hover_vars.append(_gen_variable_name(value))
    
        interactivity = [{
            'event': 'click',
            'values': click_vars
        }, {
            'event': 'hover',
            'values': hover_vars
        }]

        return interactivity

    def get_variables(self):
        variables = {}

        for value in self._click:
            name = _gen_variable_name(value)
            variables[name] = value

        for value in self._hover:
            name = _gen_variable_name(value)
            variables[name] = value

        return variables


def _gen_variable_name(value):
    return 'v' + _get_hash(value)[:6]


def _get_hash(text):
    h = hashlib.sha1()
    h.update(text.encode('utf-8'))
    return h.hexdigest()
