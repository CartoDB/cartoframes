from __future__ import absolute_import
from ..utils import defaults


class Layer(object):
    """CARTO VL layer

    Args:
        source (Source): The source data. It can be GeoJSON, SQL or Dataset.
        style (dict, tuple, list, optional): Style of the visualization. It
            can contain the following values:
        variables (list, optional): When you have to define variables to be reused. They're needed
                for showing information in popups shown by the interactivity.
        interactivity (str, list, or dict, optional): This option adds
            interactivity (click or hover) to a layer to show popups.
            Defaults to ``hover`` if one of the following inputs are specified:
                - dict: If a :obj:`dict`, this must have the key `cols` with its
                value a list of columns. Optionally add `event` to choose ``hover``
                or ``click``. Specifying a `header` key/value pair adds a header to
                the popup that will be rendered in HTML.

    Example:

        .. code::

            from cartoframes import carto_vl as vl
            from cartoframes import CartoContext

            context = CartoContext(
                base_url='https://cartovl.carto.com/',
                api_key='default_public'
            )

            vl.Map([
                vl.Layer(
                    source=vl.source.SQL('SELECT * FROM populated_places WHERE adm0name = \'Spain\''),
                    style={
                        'color': 'red'
                    }
                )],
                context=context
            )
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
