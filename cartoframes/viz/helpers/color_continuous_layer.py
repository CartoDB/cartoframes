from __future__ import absolute_import

from ..layer import Layer


def color_continuous_layer(source, value, title='', palette=None):
    """Helper function for quickly creating a continuous color map

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by
        title (str, optional): Title of legend
        palette (str, optional): Palette that can be a named cartocolor palette
          or other valid CARTO VL palette expression. Default is `bluyl`.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`. Includes Legend and
        popup on `value`.
    """
    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp(linear(${0}), {1})'.format(value, palette or 'bluyl')
            },
            'line': {
                'color': 'ramp(linear(${0}), {1})'.format(value, palette or 'bluyl')
            },
            'polygon': {
                'color': 'opacity(ramp(linear(${0}), {1}), 0.9)'.format(value, palette or 'bluyl')
            }
        },
        popup={
            'hover': {
                'title': title or value,
                'value': '$' + value
            }
        },
        legend={
            'type': {
                'point': 'color-continuous-point',
                'line': 'color-continuous-line',
                'polygon': 'color-continuous-polygon'
            },
            'title': title or value,
            'description': ''
        }
    )
