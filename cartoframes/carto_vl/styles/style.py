from ..utils import defaults


class Style(object):
    def __init__(self, style=None):
        self.style = self._init_style(style)

    def _init_style(self, style):
        """Adds style properties to the styling"""
        if style is None:
            return ''
        elif isinstance(style, dict):
            return self. _parse_style_properties_dict(style)
        elif isinstance(style, str):
            return style
        else:
            raise ValueError('`style` must be a dictionary or a viz string')

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


def _convstr(obj):
    """convert all types to strings or None"""
    return str(obj) if obj is not None else None


def _to_camel_case(text):
    """convert properties to camelCase"""
    components = text.split('-')
    return components[0] + ''.join(x.title() for x in components[1:])
