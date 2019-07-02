from __future__ import absolute_import

from . import constants
from ..utils import gen_variable_name, camel_dictionary


class Widget(object):
    """Widget

    Args:
        data (dict): The widget definition for a layer. It contains the information to render a widget:
            `type`: 'default', 'formula', time-series', 'animation', 'category', 'histogram'
            `value`: A constant value or a CARTO VL expression
            `options`: Options for the widget, this varies depending on the widget

            The widget also can display text information: `title`, `description` and `footer`.
    Example:

    .. code::

        from cartoframes.viz import Widget

        Widget({
            type: 'formula',
            value: 'viewportSum($amount)'
            title: '...',
            description: '...',
            footer: '...'
        })
    """

    def __init__(self, data=None):
        self._init_widget(data)

    def _init_widget(self, data):
        self._type = ''
        self._value = ''
        self._name = ''
        self._title = ''
        self._description = ''
        self._footer = ''
        self._options = {}
        if data is not None:
            if isinstance(data, dict):
                self._type = data.get('type', '')
                self._value = data.get('value', '')
                self._name = gen_variable_name(self._value)
                self._title = data.get('title', '')
                self._description = data.get('description', '')
                self._footer = data.get('footer', '')
                self._options = camel_dictionary(data.get('options', {}))
            else:
                raise ValueError('Wrong widget input.')

    def get_info(self):
        if self._type or self._title or self._description or self._footer:
            self._check_type()

            return {
                'type': self._type,
                'name': self._name,
                'value': self._value,
                'title': self._title,
                'description': self._description,
                'footer': self._footer,
                'has_variable': self.has_variable(),
                'options': self._options
            }
        else:
            return {}

    def has_variable(self):
        return self._type == 'formula'

    def _check_type(self):
        if self._type and self._type not in constants.WIDGET_TYPES:
            raise ValueError(
                'Widget type is not valid. Valid widget types are: {}.'.format(
                    ', '.join(constants.WIDGET_TYPES)
                ))
