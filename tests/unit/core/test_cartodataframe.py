"""Unit tests for cartoframes.data."""

import geopandas as gpd

from shapely.geometry import box

from cartoframes import CartoDataFrame

# DATA FRAME SRC BBOX
pol_1 = box(1, 1, 2, 2)
pol_2 = box(3, 3, 4, 4)
GDF_BOX = gpd.GeoDataFrame({'id': [1, 2], 'geometry': [pol_1, pol_2]}, columns=['id', 'geometry'])


class TestCartoDataFrame(object):

    def test_basic_inheritance(self):
        """Test basic inheritance"""
        cdf = CartoDataFrame(GDF_BOX)
        assert isinstance(cdf, CartoDataFrame)

    def test_crs_inheritance(self):
        """Test crs inheritance"""
        cdf = CartoDataFrame(GDF_BOX)
        cdf.crs = 'epsg:4326'
        cdf = cdf.to_crs('epsg:3857')
        assert isinstance(cdf, CartoDataFrame)
        assert cdf.crs == 'epsg:3857'

    def test_filter_inheritance(self):
        """Test filter inheritance"""
        cdf = CartoDataFrame(GDF_BOX)
        cdf = cdf[cdf.id > 1]
        assert isinstance(cdf, CartoDataFrame)
        assert len(cdf) == 1
