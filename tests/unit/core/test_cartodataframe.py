"""Unit tests for cartoframes.data."""

from pandas import concat
from geopandas import GeoDataFrame
from shapely.geometry import box, Point

from cartoframes import CartoDataFrame


class TestCartoDataFrame(object):

    def setup_method(self):
        self.gdf = GeoDataFrame(
            {
                'id': [1, 2],
                'my_geometry': [box(1, 1, 2, 2), box(3, 3, 4, 4)],
                'other_geometry': ['Point(0 0)', 'Point(1 1)']
            },
            geometry='my_geometry',
            crs='epsg:4326'
        )

    def test_constructor(self):
        cdf = CartoDataFrame(self.gdf)
        assert isinstance(cdf, CartoDataFrame)
        assert cdf._constructor == CartoDataFrame

    def test_crs_gdf(self):
        cdf = CartoDataFrame(self.gdf)
        assert cdf.crs == 'epsg:4326'

    def test_crs_custom(self):
        cdf = CartoDataFrame(self.gdf, crs='epsg:3857')
        assert cdf.crs == 'epsg:3857'

    def test_to_crs(self):
        cdf = CartoDataFrame(self.gdf)
        cdf = cdf.to_crs('epsg:3857')
        assert isinstance(cdf, CartoDataFrame)
        assert cdf.crs == 'epsg:3857'

    def test_geometry_gdf(self):
        cdf = CartoDataFrame(self.gdf)
        assert cdf.geometry.name == 'my_geometry'

    def test_geometry_custom(self):
        cdf = CartoDataFrame(self.gdf, geometry='other_geometry')
        assert cdf.geometry.name == 'other_geometry'

    def test_set_geometry(self):
        cdf = CartoDataFrame(self.gdf)
        cdf = cdf.set_geometry('other_geometry')
        assert isinstance(cdf, CartoDataFrame)
        assert cdf.geometry.name == 'other_geometry'

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
        cdf = CartoDataFrame(self.gdf)
        cdf.to_carto('table_name')
        mock.assert_called_once_with(cdf, 'table_name')

    def test_viz(self, mocker):
        mocker.patch('cartoframes.viz.Map', return_value='__map__')
        mock_layer = mocker.patch('cartoframes.viz.Layer')
        cdf = CartoDataFrame(self.gdf)
        viz = cdf.viz('__style__')
        mock_layer.assert_called_once_with(cdf, '__style__')
        assert viz == '__map__'

    def test_getitem_series(self):
        cdf = CartoDataFrame(self.gdf)
        cdf = cdf[cdf.id > 1]
        assert isinstance(cdf, CartoDataFrame)
        assert len(cdf) == 1

    def test_getitem_list(self):
        cdf = CartoDataFrame(self.gdf)
        cdf = cdf[['id']]
        assert isinstance(cdf, CartoDataFrame)
        assert len(cdf) == 2

    def test_getitem_slice(self):
        cdf = CartoDataFrame(self.gdf)
        cdf = cdf[slice(1)]
        assert isinstance(cdf, CartoDataFrame)
        assert len(cdf) == 1

    def test_astype(self):
        cdf = CartoDataFrame({'a': [1], 'geometry': [Point(0, 0)]})
        cdf = cdf.astype('object')
        assert isinstance(cdf, CartoDataFrame)

    def test_merge(self):
        cdf1 = CartoDataFrame({'lkey': ['foo', 'bar'], 'value': [1, 2]})
        cdf2 = CartoDataFrame({'rkey': ['foo', 'bar'], 'value': [5, 6]})
        cdf = cdf1.merge(cdf2, left_on='lkey', right_on='rkey')
        assert isinstance(cdf, CartoDataFrame)

    def test_dissolve(self):
        cdf = CartoDataFrame({'a': [1], 'geometry': [Point(0, 0)]})
        cdf = cdf.dissolve(by='a')
        assert isinstance(cdf, CartoDataFrame)

    def test_explode(self):
        cdf = CartoDataFrame({'a': [1], 'geometry': [Point(0, 0)]})
        cdf = cdf.explode()
        assert isinstance(cdf, CartoDataFrame)

    def test_concat(self):
        cdf1 = CartoDataFrame({'a': [1], 'geometry': [Point(0, 0)]})
        cdf2 = CartoDataFrame({'a': [2], 'geometry': [Point(1, 1)]})
        cdf = concat([cdf1, cdf2])
        assert isinstance(cdf, CartoDataFrame)
