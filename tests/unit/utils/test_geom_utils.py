"""Unit tests for cartoframes.data.utils"""

import pandas as pd
import geopandas as gpd

from shapely.geos import lgeos
from shapely.geometry import Point, base

from cartoframes.utils.geom_utils import (ENC_EWKT, ENC_SHAPELY, ENC_WKB,
                                          ENC_WKB_BHEX, ENC_WKB_HEX, ENC_WKT,
                                          decode_geometry, decode_geometry_item, detect_encoding_type)


class TestGeomUtils(object):
    """Tests for functions in data.utils module"""

    def setup_method(self):
        self.geom = [
            '010100000000000000000000000000000000000000',
            '010100000000000000000024400000000000002e40',
            '010100000000000000000034400000000000003e40'
        ]
        self.lng = [0, 10, 20]
        self.lat = [0, 15, 30]
        self.geometry = gpd.GeoSeries([
            Point([0, 0]),
            Point([10, 15]),
            Point([20, 30])
        ], name='geometry')

    def test_decode_geometry(self):
        geom = pd.Series(['POINT(0 0)', 'POINT(1 1)'])
        expected_decoded_geom = gpd.GeoSeries([Point([0, 0]), Point([1, 1])])

        decoded_geom = decode_geometry(geom)
        assert str(decoded_geom) == str(expected_decoded_geom)

    def test_decode_geometry_empty(self):
        geom_empty = gpd.GeoSeries([])
        expected_decoded_geom = gpd.GeoSeries([])

        decoded_geom = decode_geometry(geom_empty)
        assert str(decoded_geom) == str(expected_decoded_geom)

    def test_decode_geometry_none(self):
        geom_none = gpd.GeoSeries([None, None])
        expected_decoded_geom = gpd.GeoSeries([base.BaseGeometry(), base.BaseGeometry()])

        decoded_geom = decode_geometry(geom_none)
        assert str(decoded_geom) == str(expected_decoded_geom)

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
        geom = decode_geometry_item(Point(1234, 5789), ENC_SHAPELY)
        assert str(geom) == str(expected_geom)

    def test_decode_geometry_wkb(self):
        geom = decode_geometry_item(
            b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@', ENC_WKB)
        assert lgeos.GEOSGetSRID(geom._geom) == 0
        assert geom.wkb == b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@'

        geom = decode_geometry_item(
            b'\x01\x01\x00\x00 \xe6\x10\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@', ENC_WKB)  # ext
        assert lgeos.GEOSGetSRID(geom._geom) == 4326
        assert geom.wkb == b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@'

    def test_decode_geometry_wkb_hex(self):
        geom = decode_geometry_item('0101000000000000000048934000000000009DB640', ENC_WKB_HEX)
        assert lgeos.GEOSGetSRID(geom._geom) == 0
        assert geom.wkb_hex == '0101000000000000000048934000000000009DB640'

        geom = decode_geometry_item('0101000020E6100000000000000048934000000000009DB640', ENC_WKB_HEX)  # ext
        assert lgeos.GEOSGetSRID(geom._geom) == 4326
        assert geom.wkb_hex == '0101000000000000000048934000000000009DB640'

    def test_decode_geometry_wkb_bhex(self):
        geom = decode_geometry_item(b'0101000000000000000048934000000000009DB640', ENC_WKB_BHEX)
        assert lgeos.GEOSGetSRID(geom._geom) == 0
        assert geom.wkb == b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@'

        geom = decode_geometry_item(b'0101000020E6100000000000000048934000000000009DB640', ENC_WKB_BHEX)  # ext
        assert lgeos.GEOSGetSRID(geom._geom) == 4326
        assert geom.wkb == b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@'

    def test_decode_geometry_wkt(self):
        geom = decode_geometry_item('POINT (1234 5789)', ENC_WKT)
        assert lgeos.GEOSGetSRID(geom._geom) == 0
        assert geom.wkt == 'POINT (1234 5789)'

    def test_decode_geometry_ewkt(self):
        geom = decode_geometry_item('SRID=4326;POINT (1234 5789)', ENC_EWKT)  # ext
        assert lgeos.GEOSGetSRID(geom._geom) == 4326
        assert geom.wkt == 'POINT (1234 5789)'
