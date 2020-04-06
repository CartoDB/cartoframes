from .utils import get_value, prop
from ..constants import CLUSTER_KEYS, CLUSTER_OPERATIONS
from ..style import Style
from ..legends import size_continuous_legend
from ..widgets import histogram_widget
from ..popups import popup_element


def cluster_size_style(value, operation='count', resolution=32, color=None, opacity=None,
                       stroke_color=None, stroke_width=None, animate=None):
    """Helper function for quickly creating a cluster map with continuously sized points.
    Cluster operations are performed in the back-end, so this helper can be used only with
    CARTO tables or SQL queries. It cannot be used with GeoDataFrames.

    Args:
        value (str): Numeric column to aggregate.
        operation (str, optional): Cluster operation, defaults to 'count'. Other options
            available are 'avg', 'min', 'max', and 'sum'.
        resolution (int, optional): Resolution of aggregation grid cell. Set to 32 by default.
        color (str, optional): Hex, rgb or named color value. Defaults is '#FFB927' for point geometries.
        opacity (float, optional): Opacity value. Default is 0.8.
        stroke_color (str, optional): Color of the stroke on point features.
            Default is '#222'.
        stroke_width (int, optional): Size of the stroke on point features.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        cartoframes.viz.style.Style

    """
    cluster_operation = _get_cluster_operation(operation, value)
    cluster_operation_title = _get_cluster_operation_title(operation, value)
    breakpoints = _get_breakpoints(resolution)
    animation_filter = _get_animation(animate, cluster_operation)

    data = {
        'point': {
            '@size_value': 'ramp(linear({0}, viewportMIN({0}), viewportMAX({0})), [{1}])'.format(
                cluster_operation, breakpoints),
            'width': 'ramp(linear({0}, viewportMIN({0}), viewportMAX({0})), [{1}])'.format(
                cluster_operation, breakpoints),
            'color': 'opacity({0}, {1})'.format(
                color or '#FFB927', get_value(opacity, 0.8)),
            'strokeColor': get_value(stroke_color, 'strokeColor', 'point'),
            'strokeWidth': get_value(stroke_width, 'strokeWidth', 'point'),
            'filter': animation_filter,
            'resolution': '{0}'.format(resolution)
        }
    }

    return Style(
        data,
        value,
        default_legend=size_continuous_legend(title=value),
        default_widget=histogram_widget(value, title=value),
        default_popup_hover=popup_element(cluster_operation, title=cluster_operation_title),
        default_popup_click=popup_element(cluster_operation, title=cluster_operation_title)
    )


def _get_animation(animate, cluster_operation):
    return 'animation(linear({0}), 5, fade(1,1))'.format(cluster_operation) if animate else '1'


def _get_breakpoints(resolution):
    return ', '.join([
        '{0}'.format(resolution / 8),
        '{0}'.format(resolution / 2),
        '{0}'.format(resolution)
    ])


def _get_cluster_operation_title(operation, value):
    if value is not None and operation != 'count':
        return '{0} ({1})'.format(value, operation)

    return operation


def _get_cluster_operation(operation, value):
    _check_valid_operation(operation)

    if value is not None and operation != 'count':
        return '{0}({1})'.format(CLUSTER_OPERATIONS[operation], prop(value))

    return '{0}()'.format(CLUSTER_OPERATIONS[operation])


def _check_valid_operation(operation):
    valid_operations = CLUSTER_KEYS

    if operation not in valid_operations:
        err = '"{0}" is not a valid operation. Valid operations are {1}'
        raise ValueError(err.format(operation, ', '.join(valid_operations)))
