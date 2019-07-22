from __future__ import absolute_import

from ..widget import Widget


def category_widget(value, **kwargs):
    data = kwargs
    data['type'] = 'category'
    data['value'] = value
    return Widget(data)
