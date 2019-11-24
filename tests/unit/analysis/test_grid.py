# """Unit tests for cartoframes.analysis.grid"""

import geopandas as gpd
from shapely.geometry import box, shape
from cartoframes.analysis.grid import QuadGrid
from cartoframes import CartoDataFrame

# DATA FRAME SRC BBOX
pol_1 = box(1, 1, 2, 2)
pol_2 = box(3, 3, 4, 4)
GDF_BOX = gpd.GeoDataFrame({'id': [1, 2], 'geometry': [pol_1, pol_2]})

pol_geojson = {
    "type": "Polygon",
    "coordinates": [
        [
            [
                -5.899658203125,
                38.436379603
            ],
            [
                -6.690673828125,
                37.67512527892127
            ],
            [
                -6.15234375,
                37.43997405227057
            ],
            [
                -5.8447265625,
                37.70120736474139
            ],
            [
                -6.13037109375,
                37.82280243352756
            ],
            [
                -5.877685546874999,
                38.02213147353745
            ],
            [
                -6.009521484375,
                38.12591462924157
            ],
            [
                -5.5810546875,
                38.1777509666256
            ],
            [
                -5.899658203125,
                38.436379603
            ]
        ]
    ]
}

GDF_IRREGULAR = gpd.GeoDataFrame({'id': [1], 'geometry': [shape(pol_geojson)]})


class TestGrid(object):

    def test_quadgrid_polyfill_box(self, mocker):
        """cartoframes.analysis.grid.QuadGrid.polyfill"""
        cdf = QuadGrid().polyfill(GDF_BOX, 12)
        assert isinstance(cdf, gpd.GeoDataFrame)
        assert isinstance(cdf, CartoDataFrame)
        assert cdf.shape == (288, 3)
        assert cdf.crs == 'epsg:4326'

    def test_quadgrid_polyfill_pol(self, mocker):
        """cartoframes.analysis.grid.QuadGrid.polyfill"""
        cdf = QuadGrid().polyfill(GDF_IRREGULAR, 12)
        assert isinstance(cdf, gpd.GeoDataFrame)
        assert isinstance(cdf, CartoDataFrame)
        assert cdf.shape == (98, 3)
        assert cdf.crs == 'epsg:4326'
