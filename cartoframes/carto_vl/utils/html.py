from __future__ import absolute_import

from . import defaults
from cartoframes import utils
from warnings import warn
from jinja2 import Environment, PackageLoader

class HTMLMap(object):
    def __init__(self):
        self.width = None
        self.height = None
        self.srcdoc = None

        self._env = Environment(
            loader=PackageLoader('cartoframes', 'assets/templates'),
            autoescape=True
        )

        self._env.filters['quot'] = _quote_filter
        self._env.filters['iframe_size'] = _iframe_size_filter
        self._env.filters['clear_none'] = _clear_none_filter

        self.html = None
        self._template = self._env.get_template('vector/basic.html.j2')

    def set_content(
        self, size, sources, bounds, viewport=None, creds=None, basemap=None,
            _carto_vl_path=defaults._CARTO_VL_PATH, _airship_path=None):

        self.html = self._parse_html_content(
            size, sources, bounds, viewport, creds, basemap,
            _carto_vl_path, _airship_path)

    def _parse_html_content(
        self, size, sources, bounds, viewport, creds=None, basemap=None,
            _carto_vl_path=defaults._CARTO_VL_PATH, _airship_path=None):

        token = ''

        if creds is not None:
            credentials = {
                'username': creds.username(),
                'api_key': creds.key(),
                'base_url': creds.base_url()
            }
        else:
            credentials = defaults._CREDENTIALS

        if isinstance(basemap, dict):
            token = basemap.get('token', '')
            if 'style' not in basemap:
                raise ValueError(
                    'If basemap is a dict, it must have a `style` key'
                )
            if not token and basemap.get('style').startswith('mapbox://'):
                warn('A Mapbox style usually needs a token')
            basemap = basemap.get('style')

        if (_airship_path is None):
            airship_components_path = defaults._AIRSHIP_COMPONENTS_PATH
            airship_bridge_path = defaults._AIRSHIP_BRIDGE_PATH
            airship_styles_path = defaults._AIRSHIP_STYLES_PATH
            airship_icons_path = defaults._AIRSHIP_ICONS_PATH
        else:
            airship_components_path = _airship_path + defaults._AIRSHIP_SCRIPT
            airship_bridge_path = _airship_path + defaults._AIRSHIP_BRIDGE_SCRIPT
            airship_styles_path = _airship_path + defaults._AIRSHIP_STYLE
            airship_icons_path = _airship_path + defaults._AIRSHIP_ICONS_STYLE

        camera = None
        if viewport is not None:
            camera = {
                'center': _get_center(viewport),
                'zoom': viewport.get('zoom'),
                'bearing': viewport.get('bearing'),
                'pitch': viewport.get('pitch')
            }

        return self._template.render(
            width=size[0] if size is not None else None,
            height=size[1] if size is not None else None,
            sources=sources,
            basemapstyle=basemap,
            mapboxtoken=token,
            credentials=credentials,
            bounds=bounds,
            camera=camera,
            carto_vl_path=_carto_vl_path,
            airship_components_path=airship_components_path,
            airship_bridge_path=airship_bridge_path,
            airship_styles_path=airship_styles_path,
            airship_icons_path=airship_icons_path
        )

    def _repr_html_(self):
        return self.html


def _quote_filter(value):
    return utils.safe_quotes(value.unescape())


def _iframe_size_filter(value):
    if isinstance(value, str):
        return value

    return '%spx;' % value


def _clear_none_filter(value):
    return dict(filter(lambda item: item[1] is not None, value.items()))


def _get_center(center):
    if 'lng' not in center or 'lat' not in center:
        return None

    return [center.get('lng'), center.get('lat')]
