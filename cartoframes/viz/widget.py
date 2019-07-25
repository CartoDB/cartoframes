from __future__ import absolute_import

from . import constants
from ..utils import camel_dictionary, gen_variable_name


class Widget():
    """Widget

    Args:
        data (dict): The widget definition for a layer. It contains the information to render a widget:
            `type`: 'default', 'formula', time-series', 'animation', 'category', 'histogram'
            `value`: A constant value or a CARTO VL expression

            The widget also can display text information: `title`, `description` and `footer`.
    Example:

    .. code::

        from cartoframes.viz import Widget

        Widget('formula', value='viewportSum($amount)', title='...')
    """

    def __init__(self, f_arg, **kwargs):
        if isinstance(f_arg, dict):
            self._init_widget(f_arg)
        elif isinstance(f_arg, str):
            self._init_widget(kwargs, f_arg)
        else:
            raise ValueError('Wrong widget input.')

    def _init_widget(self, data, widget_type=None):
        self._type = ''
        self._value = ''
        self._variable_name = ''
        self._title = ''
        self._prop = ''
        self._description = ''
        self._footer = ''
        self._options = {}

        if data is not None:
            self._type = widget_type if widget_type else data.get('type', '')
            self._value = data.get('value', '')
            self._variable_name = gen_variable_name(self._value) if self._value else ''
            self._title = data.get('title', '')
            self._description = data.get('description', '')
            self._footer = data.get('footer', '')
            self._prop = self.get_default_prop(data)

            options = self._get_options_from_data(data)
            self._options = camel_dictionary(options)
        else:
            raise ValueError('Wrong widget input.')

    def get_default_prop(self, data):
        prop = data.get('prop', '')
        return 'filter' if self._type in ('animation', 'time-series') and not prop else prop

    def get_info(self):
        if self._type or self._title or self._description or self._footer:
            self._check_type()

            return {
                'type': self._type,
                'prop': self._prop,
                'value': self._value,
                'variable_name': self._variable_name,
                'title': self._title,
                'description': self._description,
                'footer': self._footer,
                'has_bridge': self.has_bridge(),
                'options': self._options
            }
        else:
            return {}

    def has_bridge(self):
        return self._type not in ('formula', 'default')

    def _check_type(self):
        if self._type and self._type not in constants.WIDGET_TYPES:
            raise ValueError(
                'Widget type is not valid. Valid widget types are: {}.'.format(
                    ', '.join(constants.WIDGET_TYPES)
                ))

    def _get_options_from_data(self, data):
        options = {}
        attributes = ['type', 'value', 'title', 'footer', 'prop', 'description']

        for key, value in data.items():
            if key not in attributes:
                options[key] = value

        options['read_only'] = data.get('read_only', False)
        return options
