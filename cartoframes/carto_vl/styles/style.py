from ..utils import defaults


class Style(object):
    """CARTO VL Style

    Args:
        style (dict, string): The style for a layer. It can be a dictionary or a viz string.
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
                      style=vl.Style(\"\"\"
                        color: red
                      \"\"\")
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
        return '\n'.join(
            '{name}: {value}'.format(
                name=style_prop,
                value=_convstr(style.get(style_prop))
            )
            for style_prop in style
            if style_prop in defaults._STYLE_PROPERTIES
            and style.get(style_prop) is not None
        )


def _convstr(obj):
    """convert all types to strings or None"""
    return str(obj) if obj is not None else None
