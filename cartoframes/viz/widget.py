from __future__ import absolute_import

from . import constants


class Widget(object):
    """Widget

    Args:
        data (dict): The widget definition for a layer. It contains the information to render a widget:

    Example:

    .. code::

        from cartoframes.viz import Widget

        Widget({
            type: 'formula',
            value: 'viewportSum($amount)',
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
        self._title = ''
        self._description = ''
        self._footer = ''
        if data is not None:
            if isinstance(data, dict):
                self._type = data.get('type', '')
                self._value = data.get('value', '')
                self._title = data.get('title', '')
                self._description = data.get('description', '')
                self._footer = data.get('footer', '')
            else:
                raise ValueError('Wrong widget input.')

    def get_info(self):
        if self._type or self._title or self._description or self._footer:
            self._check_type()

            return {
                'type': self._type,
                'value': self._value,
                'title': self._title,
                'description': self._description,
                'footer': self._footer
            }
        else:
            return {}

    def _check_type(self):
        if self._type and self._type not in constants.WIDGET_TYPES:
            raise ValueError(
                'Widget type is not valid. Valid widget types are: {}.'.format(
                    ', '.join(constants.WIDGET_TYPES)
                ))
