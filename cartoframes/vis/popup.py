from __future__ import absolute_import

import hashlib


class Popup(object):
    """Popup

    Args:
        

    Example:

    """

    def __init__(self, data=None):
        self.interactivity = [{
            'event': 'click',
            'values': [
                'sqrt($pop_max)'
            ]
        }, {
            'event': 'hover',
            'values': [
                '$pop_max'
            ]
        }]

        # if isinstance(data, dict):
        #     # TODO: error control

        #     if 'click' in data:
        #         self.click = data.get('click', [])

        #     if 'hover' in data:
        #         self.hover = data.get('hover', [])

        # else:
        #     raise ValueError('Wrong popup input')

    def get_variables(self):
        variables = {}

        for item in self.interactivity:
            for value in item.get('values'):
                name = self._gen_variable_name(value)
                variables[name] = value

        return variables

    def _gen_variable_name(self, value):
        return 'v' + _get_hash(value)[:6]


def _get_hash(text):
    h = hashlib.sha1()
    h.update(text.encode('utf-8'))
    return h.hexdigest()
