from __future__ import absolute_import

from .utils import get_value, get_popup
from ..layer import Layer


def size_continuous_layer(
        source, value, title='', range_min=None, range_max=None, size=None, color=None,
        opacity=None, stroke_width=None, stroke_color=None, description='', footer='',
        legend=True, popup=True, widget=False, animate=None, credentials=None):
    """Helper function for quickly creating a size symbol map with
    continuous size scaled by `value`.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend and popup hover.
        range_min (int, optional): The minimum value of the data range for the continuous
          size ramp. Defaults to the globalMIN of the dataset.
        range_max (int, optional): The maximum value of the data range for the continuous
          size ramp. Defaults to the globalMAX of the dataset.
        size (str, optiona): Min/max size array in CARTO VL syntax. Default is
          '[2, 40]' for point geometries and '[1, 10]' for lines.
        color (str, optional): Hex value, rgb expression, or other valid
          CARTO VL color. Defaults is '#FFB927' for point geometries and
          '#4CC8A3' for lines.
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
    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'

    if range_min is None:
        range_min = 'globalMIN(${0})'.format(value)

    if range_max is None:
        range_max = 'globalMAX(${0})'.format(value)

    if opacity is None:
        opacity = '0.8'

    return Layer(
        source,
        style={
            'point': {
                '@width_value': 'ramp(linear(${0}, {1}, {2}), {3})'.format(
                    value, range_min, range_max, size or [2, 40]),
                'width': 'ramp(linear(sqrt(${0}), sqrt({1}), sqrt({2})), {3})'.format(
                    value, range_min, range_max, size or [2, 40]),
                'color': 'opacity({0}, {1})'.format(
                    color or '#FFB927', opacity),
                'strokeColor': get_value(stroke_color, 'point', 'strokeColor'),
                'strokeWidth': get_value(stroke_width, 'point', 'strokeWidth'),
                'filter': animation_filter
            },
            'line': {
                '@width_value': 'ramp(linear(${0}, {1}, {2}), {3})'.format(
                    value, range_min, range_max, size or [1, 10]),
                'width': 'ramp(linear(${0}, {1}, {2}), {3})'.format(
                    value, range_min, range_max, size or [1, 10]),
                'color': 'opacity({0}, {1})'.format(
                    color or '#4CC8A3', opacity),
                'filter': animation_filter
            }
        },
        popup=popup and not animate and get_popup(
          popup, title, value, value),
        legend=legend and {
            'type': {
                'point': 'size-continuous-point',
                'line': 'size-continuous-line',
                'polygon': 'size-continuous-polygon'
            },
            'variable': 'width_value',
            'title': title or value,
            'description': description,
            'footer': footer
        },
        widgets=[
            animate and {
                'type': 'time-series',
                'value': animate,
                'title': 'Animation'
            },
            widget and {
                'type': 'histogram',
                'value': value,
                'title': 'Distribution'
            }
        ],
        credentials=credentials
    )
