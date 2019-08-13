from __future__ import absolute_import
from __future__ import division

from .utils import serialize_palette
from carto.exceptions import CartoException
from ..constants import CLUSTER_OPERATIONS
from ..layer import Layer


def cluster_color_bins_layer(
        source, operation='count', value=None, resolution=32,
        title='', palette=None, description='', footer='',
        legend=True, popup=True, widget=False, animate=None):
    """Helper function for quickly creating a color symbol map with
    color bins by cluster.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        operation (str): Cluster operation, defaults to 'count'. Other options
          available are 'avg', 'min', 'max', and 'sum'.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend.
        palette (str, optional): Palette that can be a named cartocolor palette
          or other valid CARTO VL palette expression. Default is `purpor`.
        bins: // TODO
        description (str, optional): Description text legend placed under legend title.
        footer (str, optional): Footer text placed under legend items.
        legend (bool, optional): Display map legend: "True" or "False".
          Set to "True" by default.
        popup (bool, optional): Display popups on hover and click: "True" or "False".
          Set to "True" by default.
        widget (bool, optional): Display a widget for mapped data.
          Set to "False" by default.
        animate (str, optional): Animate features by date/time or other numeric field.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`.
        Includes a legend, popup and widget on `value`.
    """

    default_palette = 'bluyl'
    cluster_operation = _get_cluster_operation(operation, value)
    cluster_operation_title = _get_cluster_operation_title(operation, value)
    breakpoints = _get_breakpoints(resolution)
    animation_filter = _get_animation(animate, cluster_operation)

    return Layer(
        source,
        style={
            'point': {
                'width': 'ramp(linear({0}, viewportMIN({1}), viewportMAX({2})), [{3}])'.format(
                    cluster_operation, cluster_operation, cluster_operation, breakpoints),
                'color': 'ramp(linear({0}, viewportMIN({1}), viewportMAX({2})), {3})'.format(
                    cluster_operation, cluster_operation, cluster_operation, serialize_palette(palette) or default_palette),
                'strokeColor': 'opacity(#222, ramp(linear(zoom(), 0, 18),[0, 0.6]))',
                'filter': animation_filter,
                'resolution': '{0}'.format(resolution)
            }
        },
        popup=popup and not animate and {
            'hover': {
                'title': title or cluster_operation_title,
                'value': cluster_operation
            }
        },
        legend=legend and {
            'type': {
                'point': 'color-bins-point'
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
        ]
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
    valid_operations = CLUSTER_OPERATIONS.keys()

    if operation not in valid_operations:
        err = '"{0}" is not a valid operation. Valid operations are {1}'
        raise CartoException(err.format(operation, ', '.join(valid_operations)))
