from warnings import warn

from jinja2 import Environment, PackageLoader

from .. import constants
from ..basemaps import Basemaps
from . import utils


class HTMLMap(object):
    def __init__(self, template_path='templates/viz/basic.html.j2'):
        self.width = None
        self.height = None
        self.srcdoc = None
        self._env = Environment(
            loader=PackageLoader('cartoframes', 'assets'),
            autoescape=True
        )

        self._env.filters['quot'] = utils.quote_filter
        self._env.filters['iframe_size'] = utils.iframe_size_filter
        self._env.filters['clear_none'] = utils.clear_none_filter

        self.html = None
        self._template = self._env.get_template(template_path)

    def set_content(
            self, size, layers, bounds, camera=None, basemap=None, show_info=None,
            theme=None, _carto_vl_path=None,
            _airship_path=None, title='CARTOframes', description=None,
            is_embed=False, is_static=False, layer_selector=False):

        self.html = self._parse_html_content(
            size, layers, bounds, camera, basemap,
            show_info, theme, _carto_vl_path, _airship_path, title, description,
            is_embed, is_static, layer_selector)

    def _parse_html_content(
            self, size, layers, bounds, camera=None,
            basemap=None, show_info=None,
            theme=None, _carto_vl_path=None, _airship_path=None,
            title=None, description=None, is_embed=False, is_static=False, layer_selector=False):

        token = ''
        basecolor = ''

        if basemap is None:
            # No basemap
            basecolor = 'white'
            basemap = ''
        elif isinstance(basemap, str):
            if basemap not in [Basemaps.voyager, Basemaps.positron, Basemaps.darkmatter]:
                # Basemap is a color
                basecolor = basemap
                basemap = ''
        elif isinstance(basemap, dict):
            token = basemap.get('token', '')
            if 'style' in basemap:
                basemap = basemap.get('style')
                if not token and basemap.get('style').startswith('mapbox://'):
                    warn('A Mapbox style usually needs a token')
            else:
                raise ValueError(
                    'If basemap is a dict, it must have a `style` key'
                )

        if _carto_vl_path is None:
            carto_vl_path = constants.CARTO_VL_URL
        else:
            carto_vl_path = _carto_vl_path + constants.CARTO_VL_DEV

        if _airship_path is None:
            airship_components_path = constants.AIRSHIP_COMPONENTS_URL
            airship_bridge_path = constants.AIRSHIP_BRIDGE_URL
            airship_module_path = constants.AIRSHIP_MODULE_URL
            airship_styles_path = constants.AIRSHIP_STYLES_URL
            airship_icons_path = constants.AIRSHIP_ICONS_URL
        else:
            airship_components_path = _airship_path + constants.AIRSHIP_COMPONENTS_DEV
            airship_bridge_path = _airship_path + constants.AIRSHIP_BRIDGE_DEV
            airship_module_path = _airship_path + constants.AIRSHIP_MODULE_DEV
            airship_styles_path = _airship_path + constants.AIRSHIP_STYLES_DEV
            airship_icons_path = _airship_path + constants.AIRSHIP_ICONS_DEV

        has_legends = any(layer['legends'] for layer in layers)
        has_widgets = any(len(layer['widgets']) != 0 for layer in layers)

        return self._template.render(
            width=size[0] if size is not None else None,
            height=size[1] if size is not None else None,
            layers=layers,
            basemap=basemap,
            basecolor=basecolor,
            mapboxtoken=token,
            bounds=bounds,
            camera=camera,
            has_legends=has_legends,
            has_widgets=has_widgets,
            show_info=show_info,
            theme=theme,
            carto_vl_path=carto_vl_path,
            airship_components_path=airship_components_path,
            airship_module_path=airship_module_path,
            airship_bridge_path=airship_bridge_path,
            airship_styles_path=airship_styles_path,
            airship_icons_path=airship_icons_path,
            title=title,
            description=description,
            is_embed=is_embed,
            is_static=is_static,
            layer_selector=layer_selector
        )

    def _repr_html_(self):
        return self.html
