from __future__ import absolute_import, division

from carto.exceptions import CartoException

from .utils import get_value, get_popup
from ..constants import CLUSTER_KEYS, CLUSTER_OPERATIONS
from ..layer import Layer


def cluster_size_layer(
        source, value=None, operation='count', resolution=32,
        title='', color=None, opacity=None,
        stroke_width=None, stroke_color=None, description='',
        footer='', legend=True, popup=True, widget=False, animate=None, credentials=None):
    """Helper function for quickly creating a cluster map with
    continuously sized points.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Numeric column to aggregate.
        operation (str, optional): Cluster operation, defaults to 'count'. Other options
          available are 'avg', 'min', 'max', and 'sum'.
        resolution (int, optional): Resolution of aggregation grid cell. Set to 32 by default.
        title (str, optional): Title of legend and hover.
        color (str, optional): Hex value, rgb expression, or other valid
          CARTO VL color. Defaults is '#FFB927' for point geometries.
        opacity (int, optional): Opacity value for point color and line features.
          Default is '0.8'.
        stroke_width (int, optional): Size of the stroke on point features.
        stroke_color (str, optional): Color of the stroke on point features.
          Default is '#222'.
        description (str, optional): Description text legend placed under legend title.
        footer (str, optional): Footer text placed under legend items.
        legend (bool, optional): Display map legend: "True" or "False".
          Set to "True" by default.
        popup (bool, optional): Display popups on hover and click: "True" or "False".
          Set to "True" by default.
        widget (bool, optional): Display a widget for mapped data.
          Set to "False" by default.
        animate (str, optional): Animate features by date/time or other numeric field.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
          A Credentials instance. This is only used for the simplified Source API.
          When a :py:class:`Source <cartoframes.viz.Source>` is pased as source,
          these credentials is simply ignored. If not provided the credentials will be
          automatically obtained from the default credentials.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`.
        Includes a legend, popup and widget on `value`.
    """

    cluster_operation = _get_cluster_operation(operation, value)
    cluster_operation_title = _get_cluster_operation_title(operation, value)
    breakpoints = _get_breakpoints(resolution)
    animation_filter = _get_animation(animate, cluster_operation)

    if opacity is None:
        opacity = '0.8'

    return Layer(
        source,
        style={
            'point': {
                'width': 'ramp(linear({0}, viewportMIN({0}), viewportMAX({0})), [{1}])'.format(
                    cluster_operation, breakpoints),
                'color': 'opacity({0}, {1})'.format(
                    color or '#FFB927', opacity),
                'strokeColor': get_value(stroke_color, 'point', 'strokeColor'),
                'strokeWidth': get_value(stroke_width, 'point', 'strokeWidth'),
                'filter': animation_filter,
                'resolution': '{0}'.format(resolution)
            }
        },
        popup=popup and not animate and get_popup(
          popup, title, cluster_operation_title, None, cluster_operation),
        legend=legend and {
            'type': {
                'point': 'size-continuous-point'
            },
            'title': title or cluster_operation_title,
            'description': description,
            'footer': footer
        },
        widgets=[
            animate and {
                'type': 'time-series',
                'value': animate,
                'title': 'Animation'
            },
            widget and value is not None and {
                'type': 'histogram',
                'value': value,
                'title': 'Distribution'
            }
        ],
        credentials=credentials
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
        return '{0}(${1})'.format(CLUSTER_OPERATIONS[operation], value)

    return '{0}()'.format(CLUSTER_OPERATIONS[operation])


def _check_valid_operation(operation):
    valid_operations = CLUSTER_KEYS

    if operation not in valid_operations:
        err = '"{0}" is not a valid operation. Valid operations are {1}'
        raise CartoException(err.format(operation, ', '.join(valid_operations)))
