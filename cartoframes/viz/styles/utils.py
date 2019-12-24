
from .. import defaults


def serialize_palette(palette):
    if isinstance(palette, (list, tuple)):
        return '[{}]'.format(','.join(palette))
    return palette


def get_value(value, default, geom_type=None):
    if value is None:
        if geom_type in ['point', 'line', 'polygon']:
            return defaults.STYLE.get(geom_type, {}).get(default)
        return default
    return value
