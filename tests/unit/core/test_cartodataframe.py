"""Unit tests for cartoframes.data."""

from shapely.geometry import box
from geopandas import GeoDataFrame

from cartoframes import CartoDataFrame

# DATA FRAME SRC BBOX
pol_1 = box(1, 1, 2, 2)
pol_2 = box(3, 3, 4, 4)
GDF_BOX = GeoDataFrame({'id': [1, 2], 'geometry': [pol_1, pol_2]}, columns=['id', 'geometry'])


class TestCartoDataFrame(object):

    def test_basic_inheritance(self):
        cdf = CartoDataFrame(GDF_BOX)
        assert isinstance(cdf, CartoDataFrame)
        assert cdf._constructor == CartoDataFrame

    def test_crs_inheritance(self):
        cdf = CartoDataFrame(GDF_BOX)
        cdf.crs = 'epsg:4326'
        cdf = cdf.to_crs('epsg:3857')
        assert isinstance(cdf, CartoDataFrame)
        assert cdf.crs == 'epsg:3857'

    def test_filter_inheritance(self):
        cdf = CartoDataFrame(GDF_BOX)
        cdf = cdf[cdf.id > 1]
        assert isinstance(cdf, CartoDataFrame)
        assert len(cdf) == 1

    def test_from_carto(self, mocker):
        mock = mocker.patch('cartoframes.io.carto.read_carto')
        CartoDataFrame.from_carto('table_name')
        mock.assert_called_once_with('table_name')

    def test_from_file(self, mocker):
        mock = mocker.patch.object(GeoDataFrame, 'from_file')
        cdf = CartoDataFrame.from_file('file_name.geojson')
        mock.assert_called_once_with('file_name.geojson')
        assert isinstance(cdf, CartoDataFrame)

    def test_from_features(self, mocker):
        mock = mocker.patch.object(GeoDataFrame, 'from_features')
        cdf = CartoDataFrame.from_features('__features__')
        mock.assert_called_once_with('__features__')
        assert isinstance(cdf, CartoDataFrame)

    def test_to_carto(self, mocker):
        mock = mocker.patch('cartoframes.io.carto.to_carto')
        cdf = CartoDataFrame(GDF_BOX)
        cdf.to_carto('table_name')
        mock.assert_called_once_with(cdf, 'table_name')

    def test_viz(self, mocker):
        mocker.patch('cartoframes.viz.Map', return_value='__map__')
        mock_layer = mocker.patch('cartoframes.viz.Layer')
        cdf = CartoDataFrame(GDF_BOX)
        viz = cdf.viz('__style__')
        mock_layer.assert_called_once_with(cdf, '__style__')
        assert viz == '__map__'
