from __future__ import absolute_import

from warnings import warn
from cartoframes import utils
from .. import defaults

import os
import json


class HTMLMap(object):
    def __init__(self):
        self.width = None
        self.height = None
        self.srcdoc = None

    def set_content(
        self, width, height, sources, bounds, creds=None, basemap=None,
            _carto_vl_path=defaults._CARTO_VL_PATH, _airship_path=None):

        html = self._parse_html_content(
            sources, bounds, creds, basemap, _carto_vl_path, _airship_path)

        self.width = width
        self.height = height
        self.srcdoc = utils.safe_quotes(html)

    def _parse_html_content(
        self, sources, bounds, creds=None, basemap=None,
            _carto_vl_path=defaults._CARTO_VL_PATH, _airship_path=None):

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
        return (defaults._HTML_TEMPLATE).format(
            width=self.width,
            height=self.height,
            srcdoc=self.srcdoc)
