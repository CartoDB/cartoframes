from __future__ import absolute_import

from . import constants


class Legend(object):
    """Legend

    Args:
        data (dict): The legend definition for a layer. It contains the information
          to show a legend "type" (color-category, color-bins, color-continuous),
          "prop" (color) and also text information: "title", "description" and "footer".

    Example:

    .. code::
        from cartoframes.viz import Legend

        Legend({
            'type': 'color-category',
            'prop': 'color',
            'title': '[TITLE]',
            'description': '[description]',
            'footer': '[footer]'
        })

    """

    def __init__(self, data=None):
        self._init_legend(data)

    def _init_legend(self, data):
        self._type = ''
        self._prop = ''
        self._title = ''
        self._description = ''
        self._footer = ''
        if data is not None:
            if isinstance(data, dict):
                self._type = data.get('type', '')
                self._prop = data.get('prop', '')
                self._title = data.get('title', '')
                self._description = data.get('description', '')
                self._footer = data.get('footer', '')

                if self._type or self._prop:
                    if not isinstance(self._type, dict) and self._type not in constants.LEGEND_TYPES:
                        raise ValueError(
                            'Legend type "{0}" is not valid. Valid legend types are: {1}'.format(
                                self._type,
                                ', '.join(constants.LEGEND_TYPES)
                            ))
                    if self._prop not in constants.LEGEND_PROPERTIES:
                        raise ValueError(
                            'Legend property "{0}" is not valid. Valid legend property are: {1}'.format(
                                self._prop,
                                ', '.join(constants.LEGEND_PROPERTIES)
                            ))

            else:
                raise ValueError('Wrong legend input')

    def get_info(self, geom_type):
        if (self._type and self._prop) or self._title or self._description or self._footer:
            _type = self._type
            if isinstance(_type, dict) and geom_type in _type:
                _type = _type.get(geom_type)
            return {
                'type': _type,
                'prop': self._prop,
                'title': self._title,
                'description': self._description,
                'footer': self._footer
            }
        else:
            return {}
