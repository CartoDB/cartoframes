from __future__ import absolute_import
from ..utils import defaults


class Layer(object):
    """CARTO VL layer

    Args:
      TODO
    Example:
      TODO
    """

    def __init__(self,
                 source,
                 style=None,
                 variables=None,
                 interactivity=None,
                 legend=None):

        self.orig_query = source.query
        self.is_basemap = False
        self.source = source  # TO DO check instance of Source
        self.bounds = source.bounds
        self.style = _parse_style_properties(style)
        self.variables = _parse_variables(variables)
        self.interactivity = _parse_interactivity(interactivity)
        self.legend = legend
        self.viz = _set_viz(self.variables, self.style)


def _convstr(obj):
    """convert all types to strings or None"""
    return str(obj) if obj is not None else None


def _to_camel_case(text):
    """convert properties to camelCase"""
    components = text.split('-')
    return components[0] + ''.join(x.title() for x in components[1:])


def _parse_style_properties(style):
    """Adds style properties to the styling"""
    if style is None:
        return ''
    elif isinstance(style, dict):
        return _parse_style_properties_dict(style)
    elif isinstance(style, (tuple, list)):
        return _parse_style_properties_list(style)
    elif isinstance(style, str):
        return style
    else:
        raise ValueError('`style` must be a dictionary, a list or a string')


def _parse_style_properties_dict(style):
    return '\n'.join(
        '{name}: {value}'.format(
          name=_to_camel_case(style_prop),
          value=_convstr(style.get(style_prop))
        )
        for style_prop in style
        if style_prop in defaults._STYLE_PROPERTIES
        and style.get(style_prop) is not None
        )


def _parse_style_properties_list(style):
    return '\n'.join(
      '{name}: {value}'.format(
          name=_to_camel_case(style_prop[0]),
          value=_convstr(style_prop[1])
      ) for style_prop in style if style_prop[0] in defaults._STYLE_PROPERTIES)


def _parse_variables(variables):
    """Adds variables to the styling"""
    if variables is None:
        return None
    elif isinstance(variables, (tuple, list)):
        return _parse_variables_list(variables)
    elif isinstance(variables, dict):
        return _parse_variables_dict(variables)
    else:
        raise ValueError('`variables` must be a list of [ name, value ]')


def _parse_variables_list(variables):
    return '\n'.join(
        '@{name}: {value}'.format(
            name=variable[0],
            value=variable[1]
        ) for variable in variables)


def _parse_variables_dict(variables):
    return '\n'.join(
        '@{name}: {value}'.format(
          name=variable,
          value=variables.get(variable)
        )
        for variable in variables)


def _parse_interactivity(interactivity):
    """Adds interactivity syntax to the styling"""
    event_default = 'hover'

    if interactivity is None:
        return None
    elif isinstance(interactivity, dict):
        return {
          'event': interactivity.get('event', event_default),
          'header': interactivity.get('header', None),
          'values': interactivity.get('values', None)
        }
    elif interactivity is True:
        return {
          'event': event_default,
        }
    else:
        raise ValueError('`interactivity` must be a dictionary')


def _set_viz(variables, style):
    if variables and style:
        return '\n'.join([variables, style])
    elif variables:
        return variables
    else:
        return style
