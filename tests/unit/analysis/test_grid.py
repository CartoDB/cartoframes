# """Unit tests for cartoframes.analysis.grid"""

import geopandas as gpd
from shapely.geometry import box
from cartoframes.analysis.grid import QuadGrid
from cartoframes import CartoDataFrame

pol_1 = box(1, 1, 2, 2)
pol_2 = box(3, 3, 4, 4)
GDF_SRC = gpd.GeoDataFrame({'id': [1, 2], 'geometry': [pol_1, pol_2]})
GDF_SRC.crs = 'epsg:4326'


class TestGrid(object):

    def test_quadgrid_polyfill(self, mocker):
        """cartoframes.analysis.grid.QuadGrid.polyfill"""

        cdf = QuadGrid().polyfill(GDF_SRC, 12)
        assert isinstance(cdf, gpd.GeoDataFrame)
        assert isinstance(cdf, CartoDataFrame)
        assert cdf.shape == (288, 3)
        assert cdf.crs == 'epsg:4326'
