from warnings import warn
from cartoframes import utils

import os
import json

_HTML_TEMPLATE = '<iframe srcdoc="{content}" width="{width}" height="{height}"></iframe>'

# CARTO VL
_DEFAULT_CARTO_VL_PATH = 'https://libs.cartocdn.com/carto-vl/v1.1.1/carto-vl.min.js'

# AIRSHIP
_AIRSHIP_SCRIPT = '/packages/components/dist/airship.js'
_AIRSHIP_BRIDGE_SCRIPT = '/packages/bridge/dist/asbridge.js'
_AIRSHIP_STYLE = '/packages/styles/dist/airship.css'
_AIRSHIP_ICONS_STYLE = '/packages/icons/dist/icons.css'

_DEFAULT_AIRSHIP_COMPONENTS_PATH = 'https://libs.cartocdn.com/airship-components/v1.0.3/airship.js'
_DEFAULT_AIRSHIP_BRIDGE_PATH = 'https://libs.cartocdn.com/airship-bridge/v1.0.3/asbridge.js'
_DEFAULT_AIRSHIP_STYLES_PATH = 'https://libs.cartocdn.com/airship-style/v1.0.3/airship.css'
_DEFAULT_AIRSHIP_ICONS_PATH = 'https://libs.cartocdn.com/airship-icons/v1.0.3/icons.css'


class HTMLMap(object):
    def __init__(self):
        self.width = None
        self.height = None
        self.content = None

    def set_content(
        self, width, height, sources, bounds, creds=None, basemap=None,
            _carto_vl_path=_DEFAULT_CARTO_VL_PATH, _airship_path=None):

        html = self._parse_html_content(
            sources, bounds, creds, basemap, _carto_vl_path, _airship_path)

        self.width = width
        self.height = height
        self.content = utils.safe_quotes(html)

    def _parse_html_content(
        self, sources, bounds, creds=None, basemap=None,
            _carto_vl_path=_DEFAULT_CARTO_VL_PATH, _airship_path=None):

        html_template = os.path.join(
            os.path.dirname(__file__), '..', '..', 'assets', 'vector.html')

        token = ''

        with open(html_template, 'r') as html_file:
            srcdoc = html_file.read()

        if creds is not None:
            credentials = {
                'username': creds.username(),
                'api_key': creds.key(),
                'base_url': creds.base_url()
            }
        else:
            credentials = {
                'username': 'cartovl',
                'api_key': 'default_public',
                'base_url': ''
            }

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
            airship_components_path = _DEFAULT_AIRSHIP_COMPONENTS_PATH
            airship_bridge_path = _DEFAULT_AIRSHIP_BRIDGE_PATH
            airship_styles_path = _DEFAULT_AIRSHIP_STYLES_PATH
            airship_icons_path = _DEFAULT_AIRSHIP_ICONS_PATH
        else:
            airship_components_path = _airship_path + _AIRSHIP_SCRIPT
            airship_bridge_path = _airship_path + _AIRSHIP_BRIDGE_SCRIPT
            airship_styles_path = _airship_path + _AIRSHIP_STYLE
            airship_icons_path = _airship_path + _AIRSHIP_ICONS_STYLE

        return srcdoc.replace('@@SOURCES@@', json.dumps(sources)) \
            .replace('@@BASEMAPSTYLE@@', basemap) \
            .replace('@@MAPBOXTOKEN@@', token) \
            .replace('@@CREDENTIALS@@', json.dumps(credentials)) \
            .replace('@@BOUNDS@@', bounds) \
            .replace('@@CARTO_VL_PATH@@', _carto_vl_path) \
            .replace('@@AIRSHIP_COMPONENTS_PATH@@', airship_components_path) \
            .replace('@@AIRSHIP_BRIDGE_PATH@@', airship_bridge_path) \
            .replace('@@AIRSHIP_STYLES_PATH@@', airship_styles_path) \
            .replace('@@AIRSHIP_ICONS_PATH@@', airship_icons_path)

    def _repr_html_(self):
        return (_HTML_TEMPLATE).format(self.width, self.height, self.content)
