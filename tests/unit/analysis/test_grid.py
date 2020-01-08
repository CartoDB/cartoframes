# """Unit tests for cartoframes.analysis.grid"""

import os
import pytest
import numpy as np

from pandas import read_csv
from geopandas import GeoDataFrame
from shapely.geometry import box, shape

from cartoframes.analysis.grid import QuadGrid
from cartoframes.utils.geom_utils import set_geometry

from geopandas.testing import assert_geodataframe_equal

# DATA FRAME SRC BBOX
pol_1 = box(1, 1, 2, 2)
pol_2 = box(3, 3, 4, 4)
GDF_BOX = GeoDataFrame({'id': [1, 2], 'geom': [pol_1, pol_2]}, columns=['id', 'geom'], geometry='geom')

pol_geojson = {
    'type': 'Polygon',
    'coordinates': [
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

GDF_IRREGULAR = GeoDataFrame({'id': [1], 'geom': [shape(pol_geojson)]}, columns=['id', 'geom'], geometry='geom')

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))


class TestGrid(object):

    def _load_test_gdf(self, fname):
        fname = os.path.join(BASE_FOLDER, fname)
        df = read_csv(fname, dtype={'id': np.int64, 'geom': object, 'quadkey': object})
        gdf = GeoDataFrame(df, crs='epsg:4326')
        set_geometry(gdf, 'geom', inplace=True)
        return gdf

    @pytest.mark.skip()
    def test_quadgrid_polyfill_box(self, mocker):
        """cartoframes.analysis.grid.QuadGrid.polyfill"""
        gdf = QuadGrid().polyfill(GDF_BOX, 12)
        assert isinstance(gdf, GeoDataFrame)

        # Check both dataframes are equals
        gdf_test = self._load_test_gdf('grid_quadkey_bbox.csv')
        assert_geodataframe_equal(gdf, gdf_test, check_less_precise=True)

    @pytest.mark.skip()
    def test_quadgrid_polyfill_pol(self, mocker):
        """cartoframes.analysis.grid.QuadGrid.polyfill"""
        gdf = QuadGrid().polyfill(GDF_IRREGULAR, 12)
        assert isinstance(gdf, GeoDataFrame)

        # Check both dataframes are equals
        gdf_test = self._load_test_gdf('grid_quadkey_pol.csv')
        assert_geodataframe_equal(gdf, gdf_test, check_less_precise=True)
