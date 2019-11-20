import re
import sys
import json
import shapely
import binascii as ba

INDEX_COL_NAMES = [
    'cartodb_id'
]

GEOM_COLUMN_NAMES = [
    'geometry',
    'the_geom',
    'wkt_geometry',
    'wkb_geometry',
    'geom',
    'wkt',
    'wkb'
]

LAT_COLUMN_NAMES = [
    'latitude',
    'lat'
]

LNG_COLUMN_NAMES = [
    'longitude',
    'lng',
    'lon',
    'long'
]

ENC_SHAPELY = 'shapely'
ENC_WKB = 'wkb'
ENC_WKB_HEX = 'wkb-hex'
ENC_WKB_BHEX = 'wkb-bhex'
ENC_WKT = 'wkt'
ENC_EWKT = 'ewkt'

if sys.version_info < (3, 0):
    ENC_WKB_BHEX = ENC_WKB_HEX

GEO_COLUMN_NAME = 'geometry'


def generate_index(dataframe, index_column, drop_index):
    index_column = _get_column(dataframe, index_column, INDEX_COL_NAMES)
    if index_column is not None:
        dataframe.set_index(index_column, inplace=True)
        if drop_index:
            del dataframe[index_column.name]
        dataframe.index.name = None


def generate_geometry(dataframe, geom_column=None, lnglat_columns=None, drop_geom=True, drop_lnglat=True):
    if GEO_COLUMN_NAME not in dataframe:
        geom_column = _get_column(dataframe, geom_column, GEOM_COLUMN_NAMES)
        if geom_column is not None:
            dataframe[GEO_COLUMN_NAME] = _compute_geometry_from_geom(geom_column)
            if drop_geom:
                del dataframe[geom_column.name]
        else:
            lng_column = _get_column(dataframe, lnglat_columns and lnglat_columns[0], LNG_COLUMN_NAMES)
            lat_column = _get_column(dataframe, lnglat_columns and lnglat_columns[1], LAT_COLUMN_NAMES)
            if lng_column is not None and lat_column is not None:
                dataframe[GEO_COLUMN_NAME] = _compute_geometry_from_lnglat(lng_column, lat_column)
                if drop_lnglat:
                    del dataframe[lng_column.name]
                    del dataframe[lat_column.name]

    if GEO_COLUMN_NAME in dataframe:
        dataframe.set_geometry(GEO_COLUMN_NAME, inplace=True)


def _compute_geometry_from_geom(geom_column):
    if geom_column.size > 0:
        first_geom = next(item for item in geom_column if item is not None)
        enc_type = detect_encoding_type(first_geom)
        return geom_column.apply(lambda g: decode_geometry(g, enc_type))
    else:
        return geom_column


def _compute_geometry_from_lnglat(lng, lat):
    return [shapely.geometry.Point(xy) for xy in zip(lng, lat)]


def _get_column(df, main=None, options=[]):
    if main is None:
        for name in options:
            if name in df:
                return df[name]
    else:
        if main in df:
            return df[main]
    return None


def _encode_decode_decorator(func):
    """decorator for encoding and decoding geoms"""
    def wrapper(*args):
        """error catching"""
        try:
            processed_geom = func(*args)
            return processed_geom
        except ImportError as err:
            raise ImportError('The Python package `shapely` needs to be '
                              'installed to encode or decode geometries. '
                              '({})'.format(err))
    return wrapper


@_encode_decode_decorator
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
                    # This is required because in P27 bytes = str
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
    return json.dumps(shapely.geometry.mapping(geom))
