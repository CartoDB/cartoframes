import time
import binascii as ba
from warnings import warn
from copy import deepcopy

from carto.exceptions import CartoException, CartoRateLimitException

from ..columns import Column

try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


DEFAULT_RETRY_TIMES = 3

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
    if dataset.table_name:
        return 'SELECT * FROM "{schema}"."{table}"'.format(
            schema=dataset.schema or dataset._get_schema() or 'public',
            table=dataset.table_name
        )


def compute_geodataframe(dataset):
    if HAS_GEOPANDAS and dataset.dataframe is not None:
        df = dataset.dataframe
        geom_column = _get_column(df, GEOM_COLUMN_NAMES)
        if geom_column is not None:
            df['geometry'] = _compute_geometry_from_geom(geom_column)
            _warn_new_geometry_column(df)
        else:
            lat_column = _get_column(df, LAT_COLUMN_NAMES)
            lng_column = _get_column(df, LNG_COLUMN_NAMES)
            if lat_column is not None and lng_column is not None:
                df['geometry'] = _compute_geometry_from_latlng(lat_column, lng_column)
                _warn_new_geometry_column(df)
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


def _warn_new_geometry_column(df):
    if 'geometry' not in df:
        warn('A new "geometry" column has been added to the original dataframe.')


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


def recursive_read(context, query, retry_times=DEFAULT_RETRY_TIMES):
    try:
        return context.copy_client.copyto_stream(query)
    except CartoRateLimitException as err:
        if retry_times > 0:
            retry_times -= 1
            warn('Read call rate limited. Waiting {s} seconds'.format(s=err.retry_after))
            time.sleep(err.retry_after)
            warn('Retrying...')
            return recursive_read(context, query, retry_times=retry_times)
        else:
            warn(('Read call was rate-limited. '
                  'This usually happens when there are multiple queries being read at the same time.'))
            raise err


def get_columns(context, query):
    col_query = '''SELECT * FROM ({query}) _q LIMIT 0'''.format(query=query)
    table_info = context.sql_client.send(col_query)
    return Column.from_sql_api_fields(table_info['fields'])


def setting_value_exception(prop, value):
    return CartoException(("Error setting {prop}. You must use the `update` method: "
                           "dataset_info.update({prop}='{value}')").format(prop=prop, value=value))


def get_public_context(context):
    api_key = 'default_public'

    public_context = deepcopy(context)
    public_context.auth_client.api_key = api_key
    public_context.auth_api_client.api_key = api_key

    return public_context
