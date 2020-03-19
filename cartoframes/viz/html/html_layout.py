from jinja2 import Environment, PackageLoader

from .. import constants
from . import utils


class HTMLLayout(object):
    def __init__(self, template_path='templates/viz/layout.html.j2'):
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

    def set_content(self, maps, size=None, show_info=None, theme=None, _carto_vl_path=None,
                    _airship_path=None, title='CARTOframes', is_embed=False,
                    is_static=False, map_height=None, full_height=False, n_size=None, m_size=None):
        self.html = self._parse_html_content(
            maps, size, show_info, theme, _carto_vl_path, _airship_path, title,
            is_embed, is_static, map_height, full_height, n_size, m_size)

    def _parse_html_content(self, maps, size, show_info=None, theme=None, _carto_vl_path=None,
                            _airship_path=None, title=None, is_embed=False, is_static=False,
                            map_height=None, full_height=False, n_size=None, m_size=None):

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

        return self._template.render(
            width=size[0] if size is not None else None,
            height=size[1] if size is not None else None,
            maps=maps,
            show_info=show_info,
            theme=theme,
            carto_vl_path=carto_vl_path,
            airship_components_path=airship_components_path,
            airship_module_path=airship_module_path,
            airship_bridge_path=airship_bridge_path,
            airship_styles_path=airship_styles_path,
            airship_icons_path=airship_icons_path,
            title=title,
            is_embed=is_embed,
            is_static=is_static,
            map_height=map_height,
            full_height=full_height,
            n=n_size,
            m=m_size
        )

    def _repr_html_(self):
        return self.html
