import re
import sys
import json
import shapely
import binascii as ba


ENC_SHAPELY = 'shapely'
ENC_WKB = 'wkb'
ENC_WKB_HEX = 'wkb-hex'
ENC_WKB_BHEX = 'wkb-bhex'
ENC_WKT = 'wkt'
ENC_EWKT = 'ewkt'

if sys.version_info < (3, 0):
    ENC_WKB_BHEX = ENC_WKB_HEX


def decode_geometry_column(geom_column):
    if geom_column.size > 0:
        first_geom = next(item for item in geom_column if item is not None)
        enc_type = detect_encoding_type(first_geom)
        return geom_column.apply(lambda g: decode_geometry(g, enc_type))
    else:
        return geom_column


def detect_encoding_type(input_geom):
    """
    Detect geometry encoding type:
    - ENC_WKB: b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@'
    - ENC_EWKB: b'\x01\x01\x00\x00 \xe6\x10\x00\x00\x00\x00\x00\x00\x00H\x93@\x00\x00\x00\x00\x00\x9d\xb6@'
    - ENC_WKB_HEX: '0101000000000000000048934000000000009DB640'
    - ENC_EWKB_HEX: '0101000020E6100000000000000048934000000000009DB640'
    - ENC_WKB_BHEX: b'0101000000000000000048934000000000009DB640'
    - ENC_EWKB_BHEX: b'0101000020E6100000000000000048934000000000009DB640'
    - ENC_WKT: 'POINT (1234 5789)'
    - ENC_EWKT: 'SRID=4326;POINT (1234 5789)'
    """
    if isinstance(input_geom, shapely.geometry.base.BaseGeometry):
        return ENC_SHAPELY

    if isinstance(input_geom, str):
        if _is_hex(input_geom):
            return ENC_WKB_HEX
        else:
            srid, geom = _extract_srid(input_geom)
            if not geom:
                return None
            if srid:
                return ENC_EWKT
            else:
                try:
                    # This is required because in Py27 bytes = str
                    _load_wkb(geom)
                    return ENC_WKB
                except Exception:
                    return ENC_WKT

    if isinstance(input_geom, bytes):
        try:
            ba.unhexlify(input_geom)
            return ENC_WKB_BHEX
        except Exception:
            return ENC_WKB

    return None


def decode_geometry(geom, enc_type):
    """Decode any geometry into a shapely geometry."""
    if geom:
        func = {
            ENC_SHAPELY: lambda: geom,
            ENC_WKB: lambda: _load_wkb(geom),
            ENC_WKB_HEX: lambda: _load_wkb_hex(geom),
            ENC_WKB_BHEX: lambda: _load_wkb_bhex(geom),
            ENC_WKT: lambda: _load_wkt(geom),
            ENC_EWKT: lambda: _load_ewkt(geom)
        }.get(enc_type)
        return func() if func else geom
    return shapely.geometry.base.BaseGeometry()


def _load_wkb(geom):
    """Load WKB or EWKB geometry."""
    return shapely.wkb.loads(geom)


def _load_wkb_hex(geom):
    """Load WKB_HEX or EWKB_HEX geometry."""
    return shapely.wkb.loads(geom, hex=True)


def _load_wkb_bhex(geom):
    """Load WKB_BHEX or EWKB_BHEX geometry.
    The geom must be converted to WKB/EWKB before loading.
    """
    return shapely.wkb.loads(ba.unhexlify(geom))


def _load_wkt(geom):
    return shapely.wkt.loads(geom)
    """Load WKT geometry."""


def _load_ewkt(egeom):
    """Load EWKT geometry.
    The SRID must be removed before loading and added after loading.
    """
    srid, geom = _extract_srid(egeom)
    ogeom = _load_wkt(geom)
    if srid:
        shapely.geos.lgeos.GEOSSetSRID(ogeom._geom, int(srid))
    return ogeom


def _is_hex(input_geom):
    return re.match(r'^[0-9a-fA-F]+$', input_geom)


def _extract_srid(egeom):
    result = re.match(r'^SRID=(\d+);(.*)$', egeom)
    if result:
        return (result.group(1), result.group(2))
    else:
        return (0, egeom)


def to_geojson(geom):
    if geom is not None and str(geom) != 'GEOMETRYCOLLECTION EMPTY':
        return json.dumps(shapely.geometry.mapping(geom), sort_keys=True)
