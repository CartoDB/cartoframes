from __future__ import absolute_import

from ..widget import Widget
from ..constants import FORMULA_OPERATIONS_VIEWPORT, FORMULA_OPERATIONS_GLOBAL


def formula_widget(value, operation=None, **kwargs):
    """Helper function for quickly creating a formula widget.

    Formula widgets calculate aggregated values ('Avg', 'Max', 'Min', 'Sum') from numeric columns
    or counts of features ('Count') in a dataset.

    A formula widget's aggregations can be calculated on 'global' or 'viewport' based values.
    If you want the values in a formula widget to update on zoom and/or pan, use viewport based aggregations.

    Args:
        value (str): Column name of the numeric value
        operation (str): attribute for widget's aggregated value ('count', 'avg', 'max', 'min', 'sum')
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom
        is_global (boolean, optional): Account for calculations based on the entire dataset ('global') vs.
            the default of 'viewport' features.

    Returns:
        cartoframes.viz.Widget: Widget with type='formula'

    Example:

        .. code::

            from cartoframes.viz import Map, Layer
            from cartoframes.viz.widgets import formula_widget

            Map(
                Layer(
                    'seattle_collisions',
                    widgets=[
                        formula_widget(
                            'count',
                            title='Number of Collisions',
                            description='Zoom and/or pan the map to update count',
                            footer='collisions in this view'
                        )
                    ]
                )
            )

        .. code::

            from cartoframes.viz import Map, Layer
            from cartoframes.viz.widgets import formula_widget

            Map(
                Layer(
                    'seattle_collisions',
                    widgets=[
                        formula_widget(
                            'pedcount',
                            'sum',
                            is_global=True,
                            title='Total Number of Pedestrians',
                            description='involved over all collisions',
                            footer='pedestrians'
                        )
                    ]
                )
            )
    """

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
            return formula_operation + '($' + value + ')'
        else:
            return '$' + value
