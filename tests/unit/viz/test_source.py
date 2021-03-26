import pytest
import numpy as np
import pandas as pd
import geopandas as gpd

from cartoframes.auth import Credentials
from cartoframes.viz.source import Source
from cartoframes.io.managers.context_manager import ContextManager


POINT = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [102.0, 0.5]
    },
    "properties": {
        "prop0": "value0"
    }
}

MULTIPOINT = {
    "type": "Feature",
    "geometry": {
        "type": "MultiPoint",
        "coordinates": [[102.0, 0.0], [103.0, 1.0]]
    },
    "properties": {
        "prop0": "value0"
    }
}

LINESTRING = {
    "type": "Feature",
    "geometry": {
        "type": "LineString",
        "coordinates": [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]]
    },
    "properties": {
        "prop0": "value0"
    }
}

MULTILINESTRING = {
    "type": "Feature",
    "geometry": {
        "type": "MultiLineString",
        "coordinates": [[[102.0, 0.0], [103.0, 1.0]], [[104.0, 0.0], [105.0, 1.0]]]
    },
    "properties": {
        "prop0": "value0"
    }
}

POLYGON = {
    "type": "Feature",
    "geometry": {
        "type": "Polygon",
        "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]
    },
    "properties": {
        "prop0": "value0"
    }
}

MULTIPOLYGON = {
    "type": "Feature",
    "geometry": {
        "type": "MultiPolygon",
        "coordinates": [[[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0]]], [[[100.0, 1.0], [100.0, 0.0], [100.0, 0.0]]]]
    },
    "properties": {
        "prop0": "value0"
    }
}

EMPTY = {
    "type": "Feature",
    "geometry": {
        "type": "GeometryCollection",
        "geometries": []
    },
    "properties": {}
}

NONE_GEOMETRY = {
    "type": "Feature",
    "geometry": None,
    "properties": {
        "prop0": "value0"
    }
}


def setup_mocks(mocker):
    mocker.patch.object(ContextManager, 'compute_query')


class TestSource(object):
    def test_is_source_defined(self):
        """Source"""
        assert Source is not None

    def test_source_get_credentials_username(self, mocker):
        """Source should return the correct credentials when username is provided"""
        setup_mocks(mocker)
        source = Source('faketable', credentials=Credentials(
            username='fakeuser', api_key='1234'))

        credentials = source.get_credentials()

        assert credentials['username'] == 'fakeuser'
        assert credentials['api_key'] == '1234'
        assert credentials['base_url'] == 'https://fakeuser.carto.com'

    def test_source_get_credentials_base_url(self, mocker):
        """Source should return the correct credentials when base_url is provided"""
        setup_mocks(mocker)
        source = Source('faketable', credentials=Credentials(
            base_url='https://fakeuser.carto.com'))

        credentials = source.get_credentials()

        assert credentials['username'] == 'user'
        assert credentials['api_key'] == 'default_public'
        assert credentials['base_url'] == 'https://fakeuser.carto.com'

    def test_source_no_credentials(self):
        """Source should raise an exception if there are no credentials"""
        with pytest.raises(ValueError) as e:
            Source('faketable')

        assert str(e.value) == ('Credentials attribute is required. '
                                'Please pass a `Credentials` instance or use '
                                'the `set_default_credentials` function.')

    def test_dates_in_source(self):
        df = pd.DataFrame({
            'date_column': ['2019-11-10', '2019-11-11'],
            'lat': [1, 2],
            'lon': [1, 2]
        })
        df['date_column'] = pd.to_datetime(df['date_column'])
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))

        assert df.dtypes['date_column'] == np.dtype('datetime64[ns]')
        source = Source(gdf)

        assert source.datetime_column_names == ['date_column']
        assert source.gdf.dtypes['date_column'] == object

    @pytest.mark.parametrize('features', [
        [POINT],
        [MULTIPOINT],
        [LINESTRING],
        [MULTILINESTRING],
        [LINESTRING, MULTILINESTRING],
        [POLYGON],
        [MULTIPOLYGON],
        [POLYGON, MULTIPOLYGON]
    ])
    def test_different_geometry_types_source(self, features):
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        gdf = gpd.GeoDataFrame.from_features(geojson)
        source = Source(gdf)

        assert len(source.gdf) == len(features)
        assert source.gdf.equals(gdf)

    @pytest.mark.parametrize('features', [
        [POINT, NONE_GEOMETRY],
        [MULTIPOINT, NONE_GEOMETRY],
        [LINESTRING, NONE_GEOMETRY],
        [MULTILINESTRING, NONE_GEOMETRY],
        [LINESTRING, MULTILINESTRING, NONE_GEOMETRY],
        [POLYGON, NONE_GEOMETRY],
        [MULTIPOLYGON, NONE_GEOMETRY],
        [POLYGON, MULTIPOLYGON, NONE_GEOMETRY]
    ])
    def test_different_geometry_types_source_plus_none(self, features):
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        gdf = gpd.GeoDataFrame.from_features(geojson)
        source = Source(gdf)

        assert len(source.gdf) == len(features) - 1

    @pytest.mark.parametrize('features', [
        [POINT, LINESTRING],
        [POINT, POLYGON],
        [LINESTRING, POLYGON],
        [POINT, LINESTRING, POLYGON],
        [MULTIPOINT, MULTILINESTRING, MULTIPOLYGON],
        [POINT, MULTIPOINT]
    ])
    def test_different_geometry_types_source_fail(self, features):
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        gdf = gpd.GeoDataFrame.from_features(geojson)

        with pytest.raises(ValueError) as e:
            Source(gdf)

        assert str(e.value).startswith('No valid geometry column types')

    def test_empty_geometries(self):
        geojson = {
            "type": "FeatureCollection",
            "features": [EMPTY, POINT, EMPTY, EMPTY, POINT, EMPTY]
        }
        gdf = gpd.GeoDataFrame.from_features(geojson)
        source = Source(gdf)

        assert len(source.gdf) == 2

    def test_nan_geometries(self):
        df = pd.DataFrame({
            'geom': ['POINT(0 0)', np.nan, np.nan, 'POINT(0 0)', None]
        })

        source = Source(df, geom_col='geom')

        assert len(source.gdf) == 2
