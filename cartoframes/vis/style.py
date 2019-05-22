from __future__ import absolute_import

from . import defaults


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
            return defaults.STYLE_DEFAULTS
        elif isinstance(data, (str, dict)):
            return data
        else:
            raise ValueError('`style` must be a string or a dictionary')

    def compute_viz(self, geom_type=None, variables={}):
        style = self._style
        if isinstance(style, dict):
            if geom_type and geom_type in style:
                style = style.get(geom_type)
            return self._parse_style_dict(style, variables)
        elif isinstance(style, str):
            return self._parse_style_str(style, variables)
        else:
            raise ValueError('`style` must be a string or a dictionary')

    def _parse_style_dict(self, style, ext_vars):
        style_vars = style.get('vars', {})
        variables = _merge_dicts(style_vars, ext_vars)

        serialized_variables = self._serialize_variables(variables)
        serialized_properties = self._serialize_properties(style)

        return serialized_variables + serialized_properties

    def _parse_style_str(self, style, ext_vars):
        serialized_variables = self._serialize_variables(ext_vars)

        return serialized_variables + style

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
            if prop not in defaults.STYLE_PROPERTIES:
                raise ValueError(
                    'Style property "{0}" is not valid. Valid style properties are: {1}'.format(
                        prop,
                        ', '.join(defaults.STYLE_PROPERTIES)
                    ))
            output += '{name}: {value}\n'.format(
                name=prop,
                value=_convstr(properties.get(prop))
            )
        return output


def _convstr(obj):
    """Converts all types to strings or None"""
    return str(obj) if obj is not None else None


def _merge_dicts(dict1, dict2):
    d = dict1.copy()
    d.update(dict2)
    return d
