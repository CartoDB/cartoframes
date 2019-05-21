from __future__ import absolute_import

from .defaults import STYLE_DEFAULTS, STYLE_PROPERTIES
from ..utils import merge_dicts


class Style(object):
    """Style

    Args:
        data (str, dict): The style for the layer. It can be a dictionary or a viz string.
          More info at
          `CARTO VL styling <https://carto.com/developers/carto-vl/guides/style-with-expressions/>`

    Example:

        String API.

        .. code::
            from cartoframes.vis import Style

            Style('color: blue')

            Style('''
                @sum: sqrt($pop_max) / 100
                @grad: [red, blue, green]
                color: ramp(globalEqIntervals($pop_min, 3), @grad)
                filter: @sum > 20
            ''')

        Dict API.

        .. code::
            from cartoframes.vis import Style

            Style({
                'color': 'blue'
            })

            Style({
                'vars': {
                    'sum': 'sqrt($pop_max) / 100',
                    'grad': '[red, blue, green]'
                },
                'color': 'ramp(globalEqIntervals($pop_min, 3), @grad)',
                'filter': '@sum > 20'
            })
    """

    def __init__(self, data=None):
        self._style = self._init_style(data)

    def _init_style(self, data):
        if data is None:
            return STYLE_DEFAULTS
        elif isinstance(data, (str, dict)):
            return data
        else:
            raise ValueError('`style` must be a string or a dictionary')

    def compute_viz(self, geom_type, variables={}):
        style = self._style
        defaults = STYLE_DEFAULTS[geom_type]
        if isinstance(style, dict):
            if geom_type in style:
                style = style.get(geom_type)
            return self._parse_style_dict(style, defaults, variables)
        elif isinstance(style, str):
            return self._parse_style_str(style, defaults, variables)
        else:
            raise ValueError('`style` must be a string or a dictionary')

    def _parse_style_dict(self, style, defaults, ext_vars):
        style_vars = style.get('vars', {})
        variables = merge_dicts(style_vars, ext_vars)

        serialized_variables = self._serialize_variables(variables)
        serialized_properties = self._serialize_properties(
            merge_dicts(defaults, style)
        )

        return serialized_variables + serialized_properties

    def _parse_style_str(self, style, defaults, ext_vars):
        # Select style defaults
        defaults = defaults.copy()
        if 'color:' in style:
            del defaults['color']
        if 'width:' in style:
            del defaults['width']
        if 'strokeWidth:' in style:
            del defaults['strokeWidth']
        if 'strokeColor:' in style:
            del defaults['strokeColor']
    
        serialized_variables = self._serialize_variables(ext_vars)
        serialized_default_properties = self._serialize_properties(defaults)

        return serialized_variables + serialized_default_properties + style

    def _serialize_variables(self, variables={}):
        output = ''
        for var in variables:
            output += '@{name}: {value}\n'.format(
                name=var,
                value=_convstr(variables.get(var))
            )
        return output

    def _serialize_properties(self, properties={}):
        output = ''
        for prop in properties:
            if prop == 'vars':
                continue
            if prop not in STYLE_PROPERTIES:
                raise ValueError(
                    'Style property "{0}" is not valid. Valid style properties are: {1}'.format(
                        prop,
                        ', '.join(STYLE_PROPERTIES)
                    ))
            output += '{name}: {value}\n'.format(
                name=prop,
                value=_convstr(properties.get(prop))
            )
        return output


def _convstr(obj):
    """Converts all types to strings or None"""
    return str(obj) if obj is not None else None
