import re
import sys
import geojson
import geopandas
import binascii as ba

from copy import deepcopy
from shapely import wkb, wkt, geometry, geos

from carto.exceptions import CartoException

from ..lib import context


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

RESERVED_GEO_COLUMN_NAME = '__carto_geometry'


def compute_query(dataset):
    if dataset.table_name:
        return 'SELECT * FROM "{schema}"."{table}"'.format(
            schema=dataset.schema or dataset._get_schema() or 'public',
            table=dataset.table_name
        )
    return ''


def compute_geodataframe(dataset):
    return geodataframe_from_dataframe(dataset.dataframe)


def reset_geodataframe(dataset):
    if dataset.dataframe is not None and RESERVED_GEO_COLUMN_NAME in dataset.dataframe:
        del dataset.dataframe[RESERVED_GEO_COLUMN_NAME]


def geodataframe_from_dataframe(dataframe):
    if dataframe is None:
        return None

    if RESERVED_GEO_COLUMN_NAME not in dataframe:
        geom_column = _get_column(dataframe, GEOM_COLUMN_NAMES)
        if geom_column is not None:
            dataframe[RESERVED_GEO_COLUMN_NAME] = _compute_geometry_from_geom(geom_column)
        else:
            lat_column = _get_column(dataframe, LAT_COLUMN_NAMES)
            lng_column = _get_column(dataframe, LNG_COLUMN_NAMES)
            if lat_column is not None and lng_column is not None:
                dataframe[RESERVED_GEO_COLUMN_NAME] = _compute_geometry_from_latlng(lat_column, lng_column)
            else:
                raise ValueError('''No geographic data found. '''
                                 '''If a geometry exists, change the column name ({0}) or '''
                                 '''ensure it is a DataFrame with a valid geometry. '''
                                 '''If there are latitude/longitude columns, rename to ({1}), ({2}).'''.format(
                                    ', '.join(GEOM_COLUMN_NAMES),
                                    ', '.join(LAT_COLUMN_NAMES),
                                    ', '.join(LNG_COLUMN_NAMES)
                                 ))

    return geopandas.GeoDataFrame(dataframe, geometry=RESERVED_GEO_COLUMN_NAME)


def _get_column(df, options):
    for name in options:
        if name in df:
            return df[name]
    return None


def _compute_geometry_from_geom(geom_column):
    if geom_column.size > 0:
        first_geom = next(item for item in geom_column if item is not None)
        enc_type = detect_encoding_type(first_geom)
        return geom_column.apply(lambda g: decode_geometry(g, enc_type))
    else:
        return geom_column


def _compute_geometry_from_latlng(lat, lng):
    return [geometry.Point(xy) for xy in zip(lng, lat)]


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
    return geometry.base.BaseGeometry()


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
    if isinstance(input_geom, geometry.base.BaseGeometry):
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
    return wkb.loads(geom)


def _load_wkb_hex(geom):
    """Load WKB_HEX or EWKB_HEX geometry."""
    return wkb.loads(geom, hex=True)


def _load_wkb_bhex(geom):
    """Load WKB_BHEX or EWKB_BHEX geometry.
    The geom must be converted to WKB/EWKB before loading.
    """
    return wkb.loads(ba.unhexlify(geom))


def _load_wkt(geom):
    """Load WKT geometry."""
    return wkt.loads(geom)


def _load_ewkt(egeom):
    """Load EWKT geometry.
    The SRID must be removed before loading and added after loading.
    """
    srid, geom = _extract_srid(egeom)
    ogeom = _load_wkt(geom)
    if srid:
        geos.lgeos.GEOSSetSRID(ogeom._geom, int(srid))
    return ogeom


def _is_hex(input_geom):
    return re.match(r'^[0-9a-fA-F]+$', input_geom)


def _extract_srid(egeom):
    result = re.match(r'^SRID=(\d+);(.*)$', egeom)
    if result:
        return (result.group(1), result.group(2))
    else:
        return (0, egeom)


def wkt_to_geojson(wkt_input):
    shapely_geom = _load_wkt(wkt_input)
    geojson_geometry = geojson.Feature(geometry=shapely_geom, properties={})

    return str(geojson_geometry.geometry)


def geojson_to_wkt(geojson_str):
    geojson_geom = geojson.loads(geojson_str)
    wkt_geometry = geometry.shape(geojson_geom)

    shapely_geom = _load_wkt(wkt_geometry.wkt)

    return shapely_geom


def setting_value_exception(prop, value):
    return CartoException(("Error setting {prop}. You must use the `update` method: "
                           "dataset_info.update({prop}='{value}')").format(prop=prop, value=value))


def get_context_with_public_creds(credentials):
    public_creds = deepcopy(credentials)
    public_creds.api_key = 'default_public'
    return context.create_context(public_creds)


def save_index_as_column(df):
    index_name = df.index.name
    if index_name is not None:
        if index_name not in df.columns:
            df.reset_index(inplace=True)
            df.set_index(index_name, drop=False, inplace=True)


def extract_viz_columns(viz):
    """Extract columns ($name) in viz"""
    columns = [RESERVED_GEO_COLUMN_NAME]
    viz_nocomments = remove_comments(viz)
    viz_columns = re.findall(r'\$([A-Za-z0-9_]+)', viz_nocomments)
    if viz_columns is not None:
        columns += viz_columns
    return columns


def remove_comments(text):
    """Remove C-style comments"""
    def replacer(match):
        s = match.group(0)
        return ' ' if s.startswith('/') else s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text).strip()
