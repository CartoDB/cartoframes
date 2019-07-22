from __future__ import absolute_import

from ..widget import Widget


def time_series_widget(value, **kwargs):
    data = kwargs
    data['type'] = 'time-series'
    data['value'] = value
    data['read_only'] = kwargs.get('read_only', False)
    return Widget(data)
