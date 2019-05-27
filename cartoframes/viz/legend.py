from __future__ import absolute_import


class Legend(object):
    """Legend

    Args:
        data (dict): 

    Example:

    """

    def __init__(self, data=None):
        self._init_legend(data)

    def _init_legend(self, data):
        self._type = 'color-category'
        self._prop = 'color'
        self._title = ''
        self._description = ''
        self._footer = ''
        if data is not None:
            if isinstance(data, dict):
                self._type = data.get('type', 'color-category')
                self._prop = data.get('prop', 'color')
                self._title = data.get('title', '')
                self._description = data.get('description', '')
                self._footer = data.get('footer', '')
            else:
                raise ValueError('Wrong legend input')

    def get_info(self, geom_type):
        _type = self._type
        if geom_type in _type:
            _type = _type.get(geom_type)
        return {
            'type': _type,
            'property': self._prop,
            'heading': self._title,
            'description': self._description,
            'source': self._footer
        }
