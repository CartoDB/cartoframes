"""Unit tests for cartoframes.data.utils"""
import unittest
import pandas as pd

from shapely.geometry import Point
from geopandas.geoseries import GeoSeries

from cartoframes.data import Dataset
from cartoframes.data.utils import compute_query, compute_geodataframe, \
    decode_geometry, detect_encoding_type

from mocks.context_mock import ContextMock


class TestDataUtils(unittest.TestCase):
    """Tests for functions in data.utils module"""

    def setUp(self):
        self.context = ContextMock(username='', api_key='1234')
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
        ], name='geometry')
        self.msg = 'No geographic data found. '
        'If a geometry exists, change the column name '
        '(geometry, the_geom, wkt_geometry, wkb_geometry, geom, wkt, wkb) '
        'or ensure it is a DataFrame with a valid geometry. '
        'If there are latitude/longitude columns, rename to '
        '(latitude, lat), (longitude, lng, lon, long).'

    def test_compute_query(self):
        """data.utils.compute_query"""
        ds = Dataset.from_table('table_name', schema='schema', context=self.context)
        query = compute_query(ds)
        self.assertEqual(query, 'SELECT * FROM "schema"."table_name"')

    def test_compute_query_default_schema(self):
        """data.utils.compute_query"""
        ds = Dataset.from_table('table_name', context=self.context)
        query = compute_query(ds)
        self.assertEqual(query, 'SELECT * FROM "public"."table_name"')

    def test_compute_geodataframe_geometry(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'geometry': self.geom}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_the_geom(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'the_geom': self.geom}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_wkt_geometry(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'wkt_geometry': self.geom}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_wkb_geometry(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'wkb_geometry': self.geom}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_geom(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'geom': self.geom}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_wkt(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'wkt': self.geom}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_wkb(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'wkb': self.geom}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_wrong(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'wrong': []}))
        with self.assertRaises(ValueError, msg=self.msg):
            compute_geodataframe(ds)

    def test_compute_geodataframe_latitude_longitude(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'latitude': self.lat, 'longitude': self.lng}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_lat_lng(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'lat': self.lat, 'lng': self.lng}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_lat_lon(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'lat': self.lat, 'lon': self.lng}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_lat_long(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'lat': self.lat, 'long': self.lng}))
        gdf = compute_geodataframe(ds)
        self.assertEqual(str(gdf.geometry), str(self.geometry))

    def test_compute_geodataframe_only_latitude(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'latitude': self.lat}))
        with self.assertRaises(ValueError, msg=self.msg):
            compute_geodataframe(ds)

    def test_compute_geodataframe_only_longitude(self):
        ds = Dataset.from_dataframe(pd.DataFrame({'longitude': self.lng}))
        with self.assertRaises(ValueError, msg=self.msg):
            compute_geodataframe(ds)

    def test_detect_encoding_type_shapely(self):
        enc_type = detect_encoding_type(Point(1234, 5789))
        self.assertEqual(enc_type, 'shapely')

    def test_detect_encoding_type_wkb(self):
        enc_type = detect_encoding_type(b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@')
        self.assertEqual(enc_type, 'wkb')

    def test_detect_encoding_type_wkb_hex(self):
        enc_type = detect_encoding_type(b'0101000000000000000048934000000000009db640')
        self.assertEqual(enc_type, 'wkb-hex')

    def test_detect_encoding_type_wkb_hex_ascii(self):
        enc_type = detect_encoding_type('0101000000000000000048934000000000009db640')
        self.assertEqual(enc_type, 'wkb-hex-ascii')

    def test_detect_encoding_type_ewkb_hex_ascii(self):
        enc_type = detect_encoding_type('SRID=4326;0101000000000000000048934000000000009db640')
        self.assertEqual(enc_type, 'ewkb-hex-ascii')

    def test_detect_encoding_type_wkt(self):
        enc_type = detect_encoding_type('POINT (1234 5789)')
        self.assertEqual(enc_type, 'wkt')

    def test_detect_encoding_type_ewkt(self):
        enc_type = detect_encoding_type('SRID=4326;POINT (1234 5789)')
        self.assertEqual(enc_type, 'ewkt')
