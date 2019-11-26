"""Unit tests for cartoframes.data."""

import geopandas as gpd
from cartoframes import CartoDataFrame
from shapely.geometry import box

# DATA FRAME SRC BBOX
pol_1 = box(1, 1, 2, 2)
pol_2 = box(3, 3, 4, 4)
GDF_BOX = gpd.GeoDataFrame({'id': [1, 2], 'geometry': [pol_1, pol_2]}, columns=['id', 'geometry'])


class TestCartoDataFrame(object):

    def test_basic_inheritance(self, mocker):
        """Test basic inheritance"""
        cdf = CartoDataFrame(GDF_BOX)
        assert isinstance(cdf, CartoDataFrame)

    def test_crs_inhericante(self, mocker):
        """Test basic inheritance"""
        cdf = CartoDataFrame(GDF_BOX)
        cdf.crs = 'epsg:4326'
        cdf = cdf.to_crs('epsg:3857')
        assert isinstance(cdf, CartoDataFrame)
        assert cdf.crs == 'epsg:3857'
