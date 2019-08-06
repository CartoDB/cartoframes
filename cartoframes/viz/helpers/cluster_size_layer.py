from __future__ import absolute_import
from ..constants import CLUSTER_OPERATIONS
from ..layer import Layer


def cluster_size_layer(
        source, operation='count', value=None, resolution=32,
        title='', size=None, color=None, description='', footer='',
        legend=True, popup=True, widget=False, animate=None):
    """Helper function for quickly creating a size symbol map with
    continuous size scaled by cluster.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend.
        size (str, optiona): Min/max size array in CARTO VL syntax. Default is
          '[2, 40]' for point geometries and '[1, 10]' for lines.
        color (str, optional): Hex value, rgb expression, or other valid
          CARTO VL color. Defaults is '#FFB927' for point geometries and
          '#4CC8A3' for lines.
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

    breakpoints = _get_breakpoints(resolution)
    cluster_operation = _get_cluster_operation(operation, value)
    cluster_operation_title = _get_cluster_operation_title(operation, value)
    animation_filter = _get_animation(animate, cluster_operation)

    return Layer(
        source,
        style={
            'point': {
                'width': 'ramp(linear({0}, viewportMIN({1}), viewportMAX({2})), [{3}])'.format(
                    cluster_operation, cluster_operation, cluster_operation, breakpoints),
                'color': 'opacity({0}, 0.8)'.format(color or '#FFB927'),
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
    if value is not None and operation != 'count':
        return '{0}(${1})'.format(CLUSTER_OPERATIONS[operation], value)

    return '{0}()'.format(CLUSTER_OPERATIONS[operation])
