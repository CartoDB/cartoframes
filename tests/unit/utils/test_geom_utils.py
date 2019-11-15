"""Unit tests for cartoframes.data.utils"""
import pandas as pd
import pytest
from geopandas.geoseries import GeoSeries
from shapely.geometry import Point
from shapely.geos import lgeos

from cartoframes.auth import Credentials
from cartoframes.data import Dataset
from cartoframes.utils.geom_utils import (ENC_EWKT, ENC_SHAPELY, ENC_WKB,
                                          ENC_WKB_BHEX, ENC_WKB_HEX, ENC_WKT,
                                          compute_geodataframe, compute_query,
                                          decode_geometry, detect_encoding_type,
                                          extract_viz_columns, remove_comments)
from tests.unit.mocks import mock_create_context


class TestDataUtils(object):
    """Tests for functions in data.utils module"""

    def setup_method(self):
        self.credentials = Credentials(username='', api_key='1234')
        self.geom = [
            '010100000000000000000000000000000000000000',
            '010100000000000000000024400000000000002e40',
            '010100000000000000000034400000000000003e40'
        ]
        self.lng = [0, 10, 20]
        self.lat = [0, 15, 30]
        self.geometry = GeoSeries([
            Point([0, 0]),
            Point([10, 15]),
            Point([20, 30])
        ], name='__carto_geometry')
        self.msg = 'No geographic data found. ' + \
            'If a geometry exists, change the column name ' + \
            '(geometry, the_geom, wkt_geometry, wkb_geometry, geom, wkt, wkb) ' + \
            'or ensure it is a DataFrame with a valid geometry. ' + \
            'If there are latitude/longitude columns, rename to ' + \
            '(latitude, lat), (longitude, lng, lon, long).'

    def test_compute_query(self, mocker):
        """data.utils.compute_query"""
        mock_create_context(mocker)
        ds = Dataset('table_name', schema='schema', credentials=self.credentials)
        query = compute_query(ds._strategy)
        assert query == 'SELECT * FROM "schema"."table_name"'

    def test_compute_query_default_schema(self, mocker):
        """data.utils.compute_query"""
        mock_create_context(mocker)
        ds = Dataset('table_name', credentials=self.credentials)
        query = compute_query(ds._strategy)
        assert query == 'SELECT * FROM "public"."table_name"'

    def test_compute_geodataframe_geometry(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'geometry': self.geom}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_the_geom(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'the_geom': self.geom}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_wkt_geometry(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'wkt_geometry': self.geom}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_wkb_geometry(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'wkb_geometry': self.geom}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_geom(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'geom': self.geom}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_wkt(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'wkt': self.geom}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_wkb(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'wkb': self.geom}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_wrong(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'wrong': []}))
        with pytest.raises(ValueError) as e:
            compute_geodataframe(ds)
        assert str(e.value) == self.msg

    def test_compute_geodataframe_latitude_longitude(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'latitude': self.lat, 'longitude': self.lng}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_lat_lng(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'lat': self.lat, 'lng': self.lng}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_lat_lon(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'lat': self.lat, 'lon': self.lng}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_lat_long(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'lat': self.lat, 'long': self.lng}))
        gdf = compute_geodataframe(ds)
        assert str(gdf.geometry) == str(self.geometry)

    def test_compute_geodataframe_only_latitude(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'latitude': self.lat}))
        with pytest.raises(ValueError) as e:
            compute_geodataframe(ds)
        assert str(e.value) == self.msg

    def test_compute_geodataframe_only_longitude(self, mocker):
        mock_create_context(mocker)
        ds = Dataset(pd.DataFrame({'longitude': self.lng}))
        with pytest.raises(ValueError) as e:
            compute_geodataframe(ds)
        assert str(e.value) == self.msg

    def test_detect_encoding_type_shapely(self):
        enc_type = detect_encoding_type(Point(1234, 5789))
        assert enc_type == ENC_SHAPELY

    def test_detect_encoding_type_wkb(self):
        enc_type = detect_encoding_type(
            b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@')
        assert enc_type == ENC_WKB

        enc_type = detect_encoding_type(
            b'\x01\x01\x00\x00 \xe6\x10\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@')  # ext
        assert enc_type == ENC_WKB

    def test_detect_encoding_type_wkb_hex(self):
        enc_type = detect_encoding_type('0101000000000000000048934000000000009db640')
        assert enc_type == ENC_WKB_HEX

        enc_type = detect_encoding_type('0101000020E6100000000000000048934000000000009DB640')  # ext
        assert enc_type == ENC_WKB_HEX

    def test_detect_encoding_type_wkb_bhex(self):
        enc_type = detect_encoding_type(b'0101000000000000000048934000000000009db640')
        assert enc_type == ENC_WKB_BHEX

        enc_type = detect_encoding_type(b'0101000020E6100000000000000048934000000000009DB640')  # ext
        assert enc_type == ENC_WKB_BHEX

    def test_detect_encoding_type_wkt(self):
        enc_type = detect_encoding_type('POINT (1234 5789)')
        assert enc_type == ENC_WKT

    def test_detect_encoding_type_ewkt(self):
        enc_type = detect_encoding_type('SRID=4326;POINT (1234 5789)')  # ext
        assert enc_type == ENC_EWKT

    def test_decode_geometry_shapely(self):
        expected_geom = Point(1234, 5789)
        geom = decode_geometry(Point(1234, 5789), ENC_SHAPELY)
        assert str(geom) == str(expected_geom)

    def test_decode_geometry_wkb(self):
        geom = decode_geometry(
            b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@', ENC_WKB)
        assert lgeos.GEOSGetSRID(geom._geom) == 0
        assert geom.wkb == b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@'

        geom = decode_geometry(
            b'\x01\x01\x00\x00 \xe6\x10\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@', ENC_WKB)  # ext
        assert lgeos.GEOSGetSRID(geom._geom) == 4326
        assert geom.wkb == b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@'

    def test_decode_geometry_wkb_hex(self):
        geom = decode_geometry('0101000000000000000048934000000000009DB640', ENC_WKB_HEX)
        assert lgeos.GEOSGetSRID(geom._geom) == 0
        assert geom.wkb_hex == '0101000000000000000048934000000000009DB640'

        geom = decode_geometry('0101000020E6100000000000000048934000000000009DB640', ENC_WKB_HEX)  # ext
        assert lgeos.GEOSGetSRID(geom._geom) == 4326
        assert geom.wkb_hex == '0101000000000000000048934000000000009DB640'

    def test_decode_geometry_wkb_bhex(self):
        geom = decode_geometry(b'0101000000000000000048934000000000009DB640', ENC_WKB_BHEX)
        assert lgeos.GEOSGetSRID(geom._geom) == 0
        assert geom.wkb == b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@'

        geom = decode_geometry(b'0101000020E6100000000000000048934000000000009DB640', ENC_WKB_BHEX)  # ext
        assert lgeos.GEOSGetSRID(geom._geom) == 4326
        assert geom.wkb == b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@'

    def test_decode_geometry_wkt(self):
        geom = decode_geometry('POINT (1234 5789)', ENC_WKT)
        assert lgeos.GEOSGetSRID(geom._geom) == 0
        assert geom.wkt == 'POINT (1234 5789)'

    def test_decode_geometry_ewkt(self):
        geom = decode_geometry('SRID=4326;POINT (1234 5789)', ENC_EWKT)  # ext
        assert lgeos.GEOSGetSRID(geom._geom) == 4326
        assert geom.wkt == 'POINT (1234 5789)'

    def test_extract_viz_columns(self):
        viz = 'color: $hello + $A_0123'
        assert 'hello' in extract_viz_columns(viz)
        assert 'A_0123' in extract_viz_columns(viz)

    def test_remove_comments(self):
        viz = """
        color: blue // This is a line comment
        /* This is a
           multiline comment */
        """
        assert remove_comments(viz) == 'color: blue'
