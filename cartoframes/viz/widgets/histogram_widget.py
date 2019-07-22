from __future__ import absolute_import

from ..widget import Widget


def histogram_widget(value, **kwargs):
    data = kwargs
    data['type'] = 'histogram'
    data['value'] = value
    data['read_only'] = kwargs.get('read_only', False)
    return Widget(data)
