from __future__ import absolute_import

from ..widget import Widget


def default_widget(**kwargs):
    data = kwargs
    data['type'] = 'default'
    return Widget(data)
