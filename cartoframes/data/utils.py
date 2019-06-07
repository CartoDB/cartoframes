import binascii as ba

try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


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


def compute_query(dataset):
    if dataset._table_name and dataset._schema:
        return 'SELECT * FROM "{0}"."{1}"'.format(dataset._schema, dataset._table_name)


def compute_geodataframe(dataset):
    if dataset.df is not None:
        df = dataset.df.copy()
        geom_column = _get_column(df, GEOM_COLUMN_NAMES)
        if geom_column is not None:
            df['geometry'] = _compute_geometry_from_geom(geom_column)
        else:
            lat_column = _get_column(df, LAT_COLUMN_NAMES)
            lng_column = _get_column(df, LNG_COLUMN_NAMES)
            if lat_column is not None and lng_column is not None:
                df['geometry'] = _compute_geometry_from_latlng(lat_column, lng_column)
            else:
                raise ValueError('''No geographic data found. '''
                                 '''If a geometry exists, change the column name ({0}) or '''
                                 '''ensure it is a DataFrame with a valid geometry. '''
                                 '''If there are latitude/longitude columns, rename to ({1}), ({2}).'''.format(
                                     ', '.join(GEOM_COLUMN_NAMES),
                                     ', '.join(LAT_COLUMN_NAMES),
                                     ', '.join(LNG_COLUMN_NAMES)
                                 ))
        return geopandas.GeoDataFrame(df)


def _get_column(df, options):
    for name in options:
        if name in df:
            return df[name]


def _compute_geometry_from_geom(geom):
    return geom.apply(decode_geometry)


def _compute_geometry_from_latlng(lat, lng):
    from shapely import geometry
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
def decode_geometry(ewkb):
    """Decode encoded wkb into a shapely geometry"""
    # it's already a shapely object
    if hasattr(ewkb, 'geom_type'):
        return ewkb

    from shapely import wkb
    from shapely import wkt
    if ewkb:
        try:
            return wkb.loads(ba.unhexlify(ewkb))
        except Exception:
            try:
                return wkb.loads(ba.unhexlify(ewkb), hex=True)
            except Exception:
                try:
                    return wkb.loads(ewkb, hex=True)
                except Exception:
                    try:
                        return wkb.loads(ewkb)
                    except Exception:
                        try:
                            return wkt.loads(ewkb)
                        except Exception:
                            pass
