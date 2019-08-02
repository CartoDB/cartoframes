from carto.exceptions import CartoException
from .map import Map
from .html.HTMLMapGrid import HTMLMapGrid


class MapGrid(object):
    def __init__(self, maps):
        self._map_grid = _init_map_grid(maps)

    def _repr_html_(self):
        self._htmlMapGrid = HTMLMapGrid()

        self._htmlMapGrid.set_content(
            maps=self._map_grid
        )

        return self._htmlMapGrid.html


def _init_map_grid(maps):
    map_grid = []

    for i, row in enumerate(maps):
        for j, viz in enumerate(row):
            if not isinstance(viz, Map):
                raise CartoException('All the elements in the MapGrid should be an instance of Map')
            else:
                map_settings = viz.get_content()
                map_grid.append(map_settings)

    return map_grid
