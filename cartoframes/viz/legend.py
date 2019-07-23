from __future__ import absolute_import

from . import constants


class Legend(object):
    """Legend

    Args:
        data (dict): The legend definition for a layer. It contains the
          information to render a legend:

          - `type`: ``color-category``, ``color-bins``, ``color-continuous``,
            ``size-bins``, or ``size-continuous``
          - `prop` (optional): ``color``, ``width``, ``strokeColor``, or ``strokeWidth``
          - `title` (optional): Title of legend
          - `description` (optional): Description in legend
          - `footer` (optional): Footer of legend. This is often used to
            attribute data sources.

    Example:

    .. code::

        from cartoframes.viz import Legend

        Legend({
            'type': 'color-category',
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
            else:
                raise ValueError('Wrong legend input.')

    def get_info(self, geom_type=None):
        if self._type or self._title or self._description or self._footer:
            _type = self._get_type(geom_type)
            _prop = self._get_prop(_type)

            return {
                'type': _type,
                'prop': _prop,
                'title': self._title,
                'description': self._description,
                'footer': self._footer
            }
        else:
            return {}

    def _get_type(self, geom_type):
        if isinstance(self._type, dict) and geom_type in self._type:
            _type = self._type.get(geom_type)
        else:
            _type = self._type

        self._check_type(_type)
        return _type

    def _get_prop(self, _type):
        if _type and not self._prop:
            _prop = self._infer_prop(_type)
        else:
            _prop = self._prop

        self._check_prop(_prop)
        return _prop

    def _check_type(self, _type):
        if _type and _type not in constants.LEGEND_TYPES:
            raise ValueError(
                'Legend type is not valid. Valid legend types are: {}.'.format(
                    ', '.join(constants.LEGEND_TYPES)
                ))

    def _check_prop(self, _prop):
        if _prop and _prop not in constants.LEGEND_PROPERTIES:
            raise ValueError(
                'Legend property is not valid. Valid legend properties are: {}.'.format(
                    ', '.join(constants.LEGEND_PROPERTIES)
                ))

    def _infer_prop(self, _type):
        if _type.startswith('color'):
            return 'color'
        elif _type.startswith('size'):
            return 'width'
