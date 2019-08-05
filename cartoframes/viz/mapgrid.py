from carto.exceptions import CartoException
from .map import Map
from .html.HTMLMapGrid import HTMLMapGrid
from . import constants


class MapGrid(object):
    def __init__(self, maps, N_SIZE=None, M_SIZE=None):
        self._map_grid = _init_map_grid(maps)
        self._N_SIZE = N_SIZE if N_SIZE is not None else len(self._map_grid)
        self._M_SIZE = M_SIZE if M_SIZE is not None else constants.DEFAULT_GRID_M_SIZE

    def _repr_html_(self):
        self._htmlMapGrid = HTMLMapGrid()
        self._htmlMapGrid.set_content(
            maps=self._map_grid,
            size=['100%', 250 * self._M_SIZE],
            n=self._N_SIZE,
            m=self._M_SIZE
        )

        return self._htmlMapGrid.html


def _init_map_grid(maps):
    map_grid = []

    for i, viz in enumerate(maps):
        if not isinstance(viz, Map):
            raise CartoException('All the elements in the MapGrid should be an instance of Map')
        else:
            map_settings = viz.get_content()
            map_settings['is_static'] = True
            map_grid.append(map_settings)

    return map_grid
