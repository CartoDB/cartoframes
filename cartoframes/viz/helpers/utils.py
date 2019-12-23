
from .. import defaults
from ..popup import Popup
from ..popups import popup_element


def serialize_palette(palette):
    if isinstance(palette, (list, tuple)):
        return '[{}]'.format(','.join(palette))
    return palette


def get_value(value, geom_type, prop):
    if value is None:
        return defaults.STYLE.get(geom_type, {}).get(prop)
    return value


def get_popup(popup=None, title=None, alt_title=None, value=None, alt_value=None, operation=None):
    if isinstance(popup, Popup):
        return popup

    popup_value = alt_value or value
    popup_title = title or alt_title

    return [popup_element(popup_value, popup_title, operation)]
