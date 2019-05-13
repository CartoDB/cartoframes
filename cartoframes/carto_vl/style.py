from __future__ import absolute_import

from .utils import defaults


class Style(object):
    """CARTO VL Style

    Args:
        style (dict, string): The style for the layer. It can be a dictionary or a viz string.
            If a dict or a string are assigned to the Layer's style, it is casted to a Style.

    Attributes:
        viz: The viz style

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
                    source=vl.source.Dataset('populated_places'),
                    style=vl.Style({
                        'color': 'red'
                    })
                )],
                context=context
            )

        .. code::
              from cartoframes import carto_vl as vl
              from cartoframes import CartoContext

              context = CartoContext(
                  base_url='https://cartovl.carto.com/',
                  api_key='default_public'
              )

              vl.Map([
                  vl.Layer(
                      source=vl.source.Dataset('populated_places'),
                      style=vl.Style('''
                        color: red
                      ''')
                  )],
                  context=context
              )
    """

    def __init__(self, style=None):
        self.viz = self._init_style(style)

    def _init_style(self, style):
        """Adds style properties to the viz"""
        if style is None:
            return ''
        elif isinstance(style, dict):
            return self._parse_style_properties_dict(style)
        elif isinstance(style, str):
            return style
        else:
            raise ValueError('`style` must be a dictionary or a viz string')

    def _parse_style_properties_dict(self, style):
        style_properties = []

        for prop in style:
            if prop in defaults._STYLE_PROPERTIES and style.get(prop) is not None:
                style_properties.append(
                    '{name}: {value}'.format(
                        name=prop,
                        value=_convstr(style.get(prop))
                    )
                )
            else:
                raise ValueError('Style property "' + prop + '" is not valid. Valid style properties are: ' +
                                 ', '.join(defaults._STYLE_PROPERTIES))

        return '\n'.join(style_properties)


def _convstr(obj):
    """Converts all types to strings or None"""
    return str(obj) if obj is not None else None
