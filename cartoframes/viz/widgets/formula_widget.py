from __future__ import absolute_import

from ..widget import Widget
from ..constants import FORMULA_OPERATIONS_VIEWPORT, FORMULA_OPERATIONS_GLOBAL


def formula_widget(value, operation=None, **kwargs):
    data = kwargs
    data['type'] = 'formula'
    is_global = kwargs.get('is_global', False)
    data['value'] = get_value_expression(operation, value, is_global)

    return Widget(data)


def get_formula_operation(operation, is_global):
    if is_global:
        return FORMULA_OPERATIONS_GLOBAL.get(operation)
    else:
        return FORMULA_OPERATIONS_VIEWPORT.get(operation)


def get_value_expression(operation, value, is_global):
    if value == 'count':
        formula_operation = get_formula_operation(value, is_global)
        return formula_operation + '()'
    else:
        if operation:
            formula_operation = get_formula_operation(operation, is_global)
            return formula_operation + '(' + value + ')'
        else:
            return value
