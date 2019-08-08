from carto.exceptions import CartoException
from .map import Map
from .html.HTMLMapGrid import HTMLMapGrid
from . import constants
from ..utils import get_center


class MapGrid(object):
    def __init__(self,
                 maps,
                 N_SIZE=None,
                 M_SIZE=None,
                 viewport=None,
                 is_static=None):
        self._map_grid = _init_map_grid(maps, is_static, viewport)
        self._N_SIZE = N_SIZE if N_SIZE is not None else len(self._map_grid)
        self._M_SIZE = M_SIZE if M_SIZE is not None else constants.DEFAULT_GRID_M_SIZE
        self._viewport = viewport
        self._is_static = is_static

    def _repr_html_(self):
        self._htmlMapGrid = HTMLMapGrid()
        self._htmlMapGrid.set_content(
            maps=self._map_grid,
            size=['100%', 250 * self._M_SIZE],
            n=self._N_SIZE,
            m=self._M_SIZE,
            is_static=self._is_static
        )

        return self._htmlMapGrid.html


def _init_map_grid(maps, is_static, viewport):
    map_grid = []

    for i, viz in enumerate(maps):
        if not isinstance(viz, Map):
            raise CartoException('All the elements in the MapGrid should be an instance of Map')
        else:
            map_settings = _get_map_settings(viz, is_static, viewport)
            map_grid.append(map_settings)

    return map_grid


def _get_map_settings(viz, is_static, viewport):
    map_settings = viz.get_content()

    map_settings['viewport'] = _get_viewport(map_settings['viewport'], viewport)
    map_settings['camera'] = _get_camera(map_settings['viewport'])
    map_settings['is_static'] = _get_is_static(map_settings['is_static'], is_static)

    return map_settings


def _get_viewport(map_settings_viewport, map_grid_viewport):
    if map_settings_viewport is not None:
        return map_settings_viewport

    return map_grid_viewport


def _get_camera(viewport):
    camera = None
    if viewport is not None:
        camera = {
            'center': get_center(viewport),
            'zoom': viewport.get('zoom'),
            'bearing': viewport.get('bearing'),
            'pitch': viewport.get('pitch')
        }
    return camera


def _get_is_static(map_settings_is_static, map_grid_is_static):
    if map_settings_is_static is not None:
        return map_settings_is_static

    return map_grid_is_static
