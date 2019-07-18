from __future__ import absolute_import

from ..widget import Widget


def animation_widget(**kwargs):
    data = kwargs
    data['type'] = 'animation'
    return Widget(data)
