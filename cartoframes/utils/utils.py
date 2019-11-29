"""general utility functions"""

from __future__ import absolute_import

import re
import sys
import gzip
import json
import base64
import decimal
import hashlib
import requests
import geopandas
import numpy as np

from functools import wraps
from warnings import catch_warnings, filterwarnings

from ..auth.credentials import Credentials

try:
    basestring
except NameError:
    basestring = str

if sys.version_info < (3, 0):
    from io import BytesIO
    from gzip import GzipFile

    def compress(data):
        buf = BytesIO()
        with GzipFile(fileobj=buf, mode='wb') as f:
            f.write(data)
        return buf.getvalue()

    gzip.compress = compress


GEOM_TYPE_POINT = 'point'
GEOM_TYPE_LINE = 'line'
GEOM_TYPE_POLYGON = 'polygon'

PG_NULL = '__null'


def map_geom_type(geom_type):
    return {
        'Point': GEOM_TYPE_POINT,
        'MultiPoint': GEOM_TYPE_POINT,
        'LineString': GEOM_TYPE_LINE,
        'MultiLineString': GEOM_TYPE_LINE,
        'Polygon': GEOM_TYPE_POLYGON,
        'MultiPolygon': GEOM_TYPE_POLYGON
    }[geom_type]


def dict_items(indict):
    """function for iterating through dict items compatible with py2 and 3

    Args:
        indict (dict): Dictionary that will be turned into items iterator
    """
    if sys.version_info >= (3, 0):
        return indict.items()
    return indict.iteritems()


def cssify(css_dict):
    """Function to get CartoCSS from Python dicts"""
    css = ''
    for key, value in dict_items(css_dict):
        css += '{key} {{ '.format(key=key)
        for field, field_value in dict_items(value):
            css += ' {field}: {field_value};'.format(field=field,
                                                     field_value=field_value)
        css += '} '
    return css.strip()


def unique_colname(suggested, existing):
    """Given a suggested column name and a list of existing names, returns
    a name that is not present at existing by prepending _ characters."""
    while suggested in existing:
        suggested = '_{0}'.format(suggested)
    return suggested


def importify_params(param_arg):
    """Convert parameter arguments to what CARTO's Import API expects"""
    if isinstance(param_arg, bool):
        return str(param_arg).lower()
    return param_arg


def join_url(*parts):
    """join parts of URL into complete url"""
    return '/'.join(str(s).strip('/') for s in parts)


def minify_sql(lines):
    """eliminate whitespace in sql queries"""
    return '\n'.join(line.strip() for line in lines)


def pgquote(string):
    """single-quotes a string if not None, else returns null"""
    return '\'{}\''.format(string) if string else 'null'


def temp_ignore_warnings(func):
    """Temporarily ignores warnings like those emitted by the carto python sdk
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """wrapper around func to filter/reset warnings"""
        with catch_warnings():
            filterwarnings('ignore')
            evaled_func = func(*args, **kwargs)
        return evaled_func
    return wrapper


def dtypes2pg(dtype):
    """Returns equivalent PostgreSQL type for input `dtype`"""
    mapping = {
        'int16': 'smallint',
        'int32': 'integer',
        'int64': 'bigint',
        'float32': 'real',
        'float64': 'double precision',
        'object': 'text',
        'bool': 'boolean',
        'datetime64[ns]': 'timestamp',
        'datetime64[ns, UTC]': 'timestamp',
    }
    return mapping.get(str(dtype), 'text')


def pg2dtypes(pgtype):
    """Returns equivalent dtype for input `pgtype`."""
    mapping = {
        'smallint': 'int16', 'int2': 'int16',
        'integer': 'int32', 'int4': 'int32', 'int': 'int32',
        'bigint': 'int64', 'int8': 'int64',
        'real': 'float32', 'float4': 'float32',
        'double precision': 'float64', 'float8': 'float64',
        'numeric': 'float64', 'decimal': 'float64',
        'text': 'object',
        'boolean': 'bool', 'bool': 'bool',
        'date': 'datetime64[D]',
        'timestamp': 'datetime64[ns]', 'timestamp without time zone': 'datetime64[ns]',
        'timestampz': 'datetime64[ns]', 'timestamp with time zone': 'datetime64[ns]',
        'USER-DEFINED': 'object',
    }
    return mapping.get(str(pgtype), 'object')


def gen_variable_name(value):
    return 'v' + get_hash(value)[:6]


def get_hash(text):
    h = hashlib.sha1()
    h.update(text.encode('utf-8'))
    return h.hexdigest()


def merge_dicts(dict1, dict2):
    d = dict1.copy()
    d.update(dict2)
    return d


def text_match(regex, text):
    return len(re.findall(regex, text, re.MULTILINE)) > 0


def camel_dictionary(dictionary):
    snake_keys = filter(in_snake_case, dictionary.keys())

    for snake_key in snake_keys:
        dictionary[snake_to_camel(snake_key)] = dictionary.pop(snake_key)

    return dictionary


# https://stackoverflow.com/questions/19053707/converting-snake-case-to-lower-camel-case-lowercamelcase
def snake_to_camel(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + ''.join(x.title() for x in components[1:])


def in_snake_case(str):
    return str.find('_') != -1


def debug_print(verbose=0, **kwargs):
    if verbose <= 0:
        return

    for key, value in dict_items(kwargs):
        if isinstance(value, requests.Response):
            str_value = ("status_code: {status_code}, "
                         "content: {content}").format(
                             status_code=value.status_code,
                             content=value.content)
        else:
            str_value = str(value)
        if verbose < 2 and len(str_value) > 300:
            str_value = '{}\n\n...\n\n{}'.format(str_value[:250], str_value[-50:])
        print('{key}: {value}'.format(key=key, value=str_value))


def load_geojson(input_data):
    if isinstance(input_data, str):
        # File name
        data = geopandas.read_file(input_data)

    elif isinstance(input_data, list):
        # List of features
        data = geopandas.GeoDataFrame.from_features(input_data)

    elif isinstance(input_data, dict):
        # GeoJSON object
        if input_data.get('features'):
            # From features
            data = geopandas.GeoDataFrame.from_features(input_data['features'])
        elif input_data.get('type') == 'Feature':
            # From feature
            data = geopandas.GeoDataFrame.from_features([input_data])
        elif input_data.get('type'):
            # From geometry
            data = geopandas.GeoDataFrame.from_features([{
                'type': 'Feature',
                'properties': {},
                'geometry': input_data
            }])
        else:
            data = geopandas.GeoDataFrame()

    else:
        raise ValueError(
            '''
            GeoJSON source only works with GeoDataFrames from
            the geopandas package http://geopandas.org/data_structures.html#geodataframe
            ''')

    return data


def get_geodataframe_bounds(gdf):
    filtered_geometries = _filter_null_geometries(gdf)
    xmin, ymin, xmax, ymax = filtered_geometries.total_bounds

    return [[xmin, ymin], [xmax, ymax]]


def get_geodataframe_geom_type(gdf):
    if not gdf.empty and hasattr(gdf, 'geometry') and len(gdf.geometry) > 0:
        geometry = _first_value(gdf.geometry)
        if geometry and geometry.geom_type:
            return map_geom_type(geometry.geom_type)
    return None


# Dup
def _first_value(series):
    series = series.loc[~series.isnull()]  # Remove null values
    if len(series) > 0:
        return series.iloc[0]
    return None


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(CustomJSONEncoder, self).default(o)


def encode_geodataframe(data):
    filtered_geometries = _filter_null_geometries(data)
    data = _set_time_cols_epoc(filtered_geometries).to_json(cls=CustomJSONEncoder, separators=(',', ':'))
    compressed_data = gzip.compress(data.encode('utf-8'))
    return base64.b64encode(compressed_data).decode('utf-8')


def _filter_null_geometries(data):
    return data[~data.geometry.isna()]


def _set_time_cols_epoc(geometries):
    include = ['datetimetz', 'datetime', 'timedelta']

    for column in geometries.select_dtypes(include=include).columns:
        geometries[column] = geometries[column].astype(np.int64)

    return geometries


def is_sql_query(data):
    return isinstance(data, str) and re.match(r'^\s*(WITH|SELECT)\s+', data, re.IGNORECASE)


def is_geojson_file(data):
    return re.match(r'^.*\.(geojson|json)\s*$', data, re.IGNORECASE)


def is_geojson_file_path(data):
    return is_geojson_file(data)


def is_geojson(data):
    return isinstance(data, (list, dict)) or (isinstance(data, str) and is_geojson_file_path(data))


def is_table_name(data):
    # avoid circular dependecies
    from .columns import normalize_name
    return isinstance(data, str) and normalize_name(data) == data


def check_credentials(credentials):
    if not isinstance(credentials, Credentials):
        raise AttributeError('Credentials attribute is required. '
                             'Please pass a `Credentials` instance '
                             'or use the `set_default_credentials` function.')


def get_center(center):
    if 'lng' not in center or 'lat' not in center:
        return None

    return [center.get('lng'), center.get('lat')]


def remove_column_from_dataframe(dataframe, name):
    """Removes a column or index (or both) from a DataFrames"""
    if name in dataframe.columns:
        del dataframe[name]
    if dataframe.index.name == name:
        dataframe.reset_index(inplace=True)
        del dataframe[name]


def encode_row(row):
    if row is None:
        row = PG_NULL

    elif isinstance(row, float):
        if str(row) == 'inf':
            row = 'Infinity'
        elif str(row) == '-inf':
            row = '-Infinity'
        elif str(row) == 'nan':
            row = 'NaN'

    elif isinstance(row, type(b'')):
        # Decode the input if it's a bytestring
        row = row.decode('utf-8')

    special_keys = ['"', '|', '\n']
    if isinstance(row, basestring) and any(key in row for key in special_keys):
        # If the input contains any special key:
        # - replace " by ""
        # - cover the row with "..."
        row = '"{}"'.format(row.replace('"', '""'))

    return '{}'.format(row).encode('utf-8')


def extract_viz_columns(viz):
    """Extract columns ($name) in viz"""
    columns = []
    viz_nocomments = remove_comments(viz)
    viz_columns = re.findall(r'\$([A-Za-z0-9_]+)', viz_nocomments)
    if viz_columns is not None:
        columns += viz_columns
    return list(set(columns))


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
