"""general utility functions"""

from __future__ import absolute_import

import os
import re
import sys
import base64
import hashlib
import requests
import numpy as np

from functools import wraps
from warnings import filterwarnings, catch_warnings

GEOM_TYPE_POINT = 'point'
GEOM_TYPE_LINE = 'line'
GEOM_TYPE_POLYGON = 'polygon'


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


def safe_quotes(text, escape_single_quotes=False):
    """htmlify string"""
    if isinstance(text, str):
        safe_text = text.replace('"', "&quot;")
        if escape_single_quotes:
            safe_text = safe_text.replace("'", "&#92;'")
        return safe_text.replace('True', 'true')
    return text


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


# schema definition functions
def dtypes2pg(dtype):
    """Returns equivalent PostgreSQL type for input `dtype`"""
    mapping = {
        'float64': 'numeric',
        'int64': 'numeric',
        'float32': 'numeric',
        'int32': 'numeric',
        'object': 'text',
        'bool': 'boolean',
        'datetime64[ns]': 'timestamp',
    }
    return mapping.get(str(dtype), 'text')


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


def get_query_geom_type(context, query):
    """Fetch geom type of a remote table"""
    distict_query = '''
        SELECT distinct ST_GeometryType(the_geom) AS geom_type
        FROM ({}) q
        LIMIT 5
    '''.format(query)
    response = context.execute_query(distict_query, do_post=False)
    if response and response.get('rows') and len(response.get('rows')) > 0:
        st_geom_type = response.get('rows')[0].get('geom_type')
        if st_geom_type:
            return map_geom_type(st_geom_type[3:])


def get_query_bounds(context, query):
    extent_query = '''
        SELECT ARRAY[
            ARRAY[st_xmin(geom_env), st_ymin(geom_env)],
            ARRAY[st_xmax(geom_env), st_ymax(geom_env)]
        ] bounds FROM (
            SELECT ST_Extent(the_geom) geom_env
            FROM ({}) q
        ) q;
    '''.format(query)
    response = context.execute_query(extent_query, do_post=False)
    if response and response.get('rows') and len(response.get('rows')) > 0:
        return response.get('rows')[0].get('bounds')


def load_geojson(input_data):
    try:
        import geopandas
        HAS_GEOPANDAS = True
    except ImportError:
        HAS_GEOPANDAS = False

    if not HAS_GEOPANDAS:
        raise ValueError(
            '''
            GeoJSON source only works with GeoDataFrames from
            the geopandas package http://geopandas.org/data_structures.html#geodataframe
            ''')

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
        raise ValueError(
            '''
            GeoJSON source only works with GeoDataFrames from
            the geopandas package http://geopandas.org/data_structures.html#geodataframe
            ''')

    return data


def get_geodataframe_bounds(data):
    filtered_geometries = _filter_null_geometries(data)
    xmin, ymin, xmax, ymax = filtered_geometries.total_bounds

    return [[xmin, ymin], [xmax, ymax]]


def encode_geodataframe(data):
    filtered_geometries = _filter_null_geometries(data)
    data = _set_time_cols_epoc(filtered_geometries).to_json()
    encoded_data = base64.b64encode(data.encode('utf-8')).decode('utf-8')

    return encoded_data


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
    return is_geojson_file(data) and os.path.exists(data)


def is_geojson(data):
    return isinstance(data, (list, dict)) or (isinstance(data, str) and is_geojson_file_path(data))


def is_table_name(data):
    # avoid circular dependecies
    from .data.columns import normalize_name
    return isinstance(data, str) and normalize_name(data) == data
