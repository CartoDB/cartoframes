import binascii as ba

try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


def compute_query(dataset):
    if dataset.table_name and dataset.schema:
        return 'SELECT * FROM "{0}"."{1}"'.format(dataset.schema, dataset.table_name)


def compute_geodataframe(dataset):
    if dataset.df is not None:
        df = dataset.df.copy()
        geom_column = _get_geom_column(df)
        if geom_column is not None:
            df['geometry'] = _compute_geometry_from_geom(geom_column)
        else:
            lat_column = _get_lat_column(df)
            lng_column = _get_lng_column(df)
            if lat_column is not None and lng_column is not None:
                df['geometry'] = _compute_geometry_from_latlng(lat_column, lng_column)
            else:
                raise ValueError('DataFrame has no geographic data.')
        return geopandas.GeoDataFrame(df)


def _get_geom_column(df):
    if 'geometry' in df:
        return df['geometry']
    if 'the_geom' in df:
        return df['the_geom']
    if 'wkt_geometry' in df:
        return df['wkt_geometry']
    if 'wkb_geometry' in df:
        return df['wkb_geometry']
    if 'geom' in df:
        return df['geom']
    if 'wkt' in df:
        return df['wkt']
    if 'wkb' in df:
        return df['wkb']


def _get_lat_column(df):
    if 'latitude' in df:
        return df['latitude']
    if 'lat' in df:
        return df['lat']


def _get_lng_column(df):
    if 'longitude' in df:
        return df['longitude']
    if 'lng' in df:
        return df['lng']
    if 'lon' in df:
        return df['lon']
    if 'long' in df:
        return df['long']


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
    return None
