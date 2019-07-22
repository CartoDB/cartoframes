from __future__ import absolute_import

from ..widget import Widget
from ..constants import FORMULA_OPERATIONS_VIEWPORT, FORMULA_OPERATIONS_GLOBAL


def formula_widget(value, operation='count', **kwargs):
    data = kwargs
    data['type'] = 'formula'
    is_global = kwargs.get('global', False)
    operation = FORMULA_OPERATIONS_GLOBAL.get(operation) if is_global else FORMULA_OPERATIONS_VIEWPORT.get(operation)
    data['value'] = operation + '(' + value + ')'

    return Widget(data)
