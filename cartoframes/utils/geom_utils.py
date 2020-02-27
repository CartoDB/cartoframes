import re
import json
import shapely
import binascii as ba

from geopandas import GeoSeries, GeoDataFrame, points_from_xy

ENC_SHAPELY = 'shapely'
ENC_WKB = 'wkb'
ENC_WKB_HEX = 'wkb-hex'
ENC_WKB_BHEX = 'wkb-bhex'
ENC_WKT = 'wkt'
ENC_EWKT = 'ewkt'
SPHERICAL_TOLERANCE = 0.0001
SIMPLIFY_TOLERANCE = 0.001


def set_geometry(gdf, col, drop=False, inplace=False, crs=None):
    """Set the GeoDataFrame geometry using either an existing column or the specified input.
    By default yields a new object. The original geometry column is replaced with the input.
    It detects the geometry encoding and it decodes the column if required. Supported geometry
    encodings are:

        - `WKB` (Bytes, Hexadecimal String, Hexadecimal Bytestring)
        - `Extended WKB` (Bytes, Hexadecimal String, Hexadecimal Bytestring)
        - `WKT` (String)
        - `Extended WKT` (String)

    Args:
        col (column label or array): Name of the column or column containing the geometry.
        drop (boolean, default False): Delete the column to be used as the new geometry.
        inplace (boolean, default False): Modify the GeoDataFrame in place (do not create a new object).
        crs (str/result of fion.get_crs, optional): Coordinate system to use. If passed, overrides both
            DataFrame and col's crs. Otherwise, tries to get crs from passed col values or DataFrame.

    Example:
        >>> set_geometry(gdf, 'the_geom', drop=True, inplace=True)

    """
    if not isinstance(gdf, GeoDataFrame):
        raise ValueError('gdf must be an instance of geopandas.GeoDataFrame.')

    if inplace:
        frame = gdf
    else:
        frame = gdf.copy()

    # Decode geometry
    if isinstance(col, str):
        if col not in frame:
            raise Exception('Column "{0}" does not exist.'.format(col))
        frame[col] = decode_geometry(frame[col])
    else:
        col = decode_geometry(col)

    # Call set_geometry with decoded column
    frame.set_geometry(col, drop=drop, inplace=True, crs=crs)

    if not inplace:
        return frame


def set_geometry_from_xy(gdf, x, y, drop=False, inplace=False, crs=None):
    """Set the GeoDataFrame geometry using either existing lng/lat columns or the specified inputs.
    By default yields a new object. The original geometry column is replaced with the new one.

    Args:
        x (column label or array): Name of the x (longitude) column or column containing the x coordinates.
        y (column label or array): Name of the y (latitude) column or column containing the y coordinates.
        drop (boolean, default False): Delete the columns to be used to generate the new geometry.
        inplace (boolean, default False): Modify the GeoDataFrame in place (do not create a new object).
        crs (str/result of fion.get_crs, optional): Coordinate system to use. If passed, overrides both
            DataFrame and col's crs. Otherwise, tries to get crs from passed col values or DataFrame.

    Example:
        >>> set_geometry_from_xy(gdf, 'lng', 'lat', drop=True, inplace=True)

    """
    if not isinstance(gdf, GeoDataFrame):
        raise ValueError('gdf must be an instance of geopandas.GeoDataFrame.')

    if isinstance(x, str) and x in gdf and isinstance(y, str) and y in gdf:
        x_col = gdf[x]
        y_col = gdf[y]
    else:
        x_col = x
        y_col = y

    # Generate geometry
    geom_col = points_from_xy(x_col, y_col)

    # Call set_geometry with generated column
    frame = gdf.set_geometry(geom_col, inplace=inplace, crs=crs)

    if drop:
        if frame is None:
            frame = gdf
        del frame[x]
        del frame[y]

    return frame


def has_geometry(gdf):
    """Method to check if the GeoDataFrame contains a valid geometry column.
    If there is no valid geometry, you can use the following methods:

        - `set_geometry`: to create a decoded geometry column from any raw geometry column.
        - `set_geometry_from_xy`: to create a geometry column from `longitude` and `latitude` columns.
    """
    return hasattr(gdf, '_geometry_column_name') and gdf._geometry_column_name in gdf


def decode_geometry(geom_col):
    """Decodes a DataFrame column. It detects the geometry encoding and it decodes the column if required.
    Supported geometry encodings are:

        - `WKB` (Bytes, Hexadecimal String, Hexadecimal Bytestring)
        - `Extended WKB` (Bytes, Hexadecimal String, Hexadecimal Bytestring)
        - `WKT` (String)
        - `Extended WKT` (String)

    Args:
        geom_col (array): Column containing the encoded geometry.

    Example:
        >>> decode_geometry(df['the_geom'])

    """
    if geom_col.size > 0:
        enc_type = None
        if any(geom_col):
            first_geom = next(item for item in geom_col if item is not None)
            enc_type = detect_encoding_type(first_geom)
        return GeoSeries(geom_col.apply(lambda g: decode_geometry_item(g, enc_type)))
    else:
        return geom_col


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
                return ENC_WKT

    if isinstance(input_geom, bytes):
        try:
            ba.unhexlify(input_geom)
            return ENC_WKB_BHEX
        except Exception:
            return ENC_WKB

    return None


def decode_geometry_item(geom, enc_type):
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
    """Load WKT geometry."""
    return shapely.wkt.loads(geom)


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


def encode_geometry_ewkt(geom, srid=4326):
    if isinstance(geom, shapely.geometry.base.BaseGeometry):
        return 'SRID={0};{1}'.format(srid, geom.wkt)


def encode_geometry_ewkb(geom, srid=4326):
    if isinstance(geom, shapely.geometry.base.BaseGeometry):
        shapely.geos.lgeos.GEOSSetSRID(geom._geom, srid)
        return shapely.wkb.dumps(geom, hex=True, include_srid=True)


def to_geojson(geom, buffer_simplify=True):
    if geom is not None and str(geom) != 'GEOMETRYCOLLECTION EMPTY':
        if buffer_simplify and geom.geom_type in ('Polygon', 'MultiPolygon'):
            return json.dumps(shapely.geometry.mapping(
                geom.buffer(SPHERICAL_TOLERANCE).simplify(SIMPLIFY_TOLERANCE)
            ), sort_keys=True)
        else:
            return json.dumps(shapely.geometry.mapping(geom), sort_keys=True)
