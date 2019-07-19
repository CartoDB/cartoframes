from __future__ import absolute_import

from ..widget import Widget


def formula_widget(value, **kwargs):
    data = kwargs
    data['type'] = 'formula'
    data['value'] = value

    return Widget(data)
