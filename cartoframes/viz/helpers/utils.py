
from .. import defaults


def serialize_palette(palette):
    if isinstance(palette, (list, tuple)):
        return '[{}]'.format(','.join(palette))
    return palette


def get_value(value, geom_type, prop):
    if value is None:
        return defaults.STYLE.get(geom_type, {}).get(prop)
    return value
