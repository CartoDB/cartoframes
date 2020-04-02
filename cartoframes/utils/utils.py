"""general utility functions"""

import os
import re
import gzip
import json
import time
import base64
import appdirs
import decimal
import hashlib
import inspect
import requests
import geopandas
import numpy as np
import pkg_resources
import semantic_version

from functools import wraps
from datetime import datetime, timezone
from warnings import catch_warnings, filterwarnings
from pyrestcli.exceptions import ServerErrorException
from pandas.api.types import is_datetime64_any_dtype as is_datetime

from .logger import log
from ..exceptions import DOError

GEOM_TYPE_POINT = 'point'
GEOM_TYPE_LINE = 'line'
GEOM_TYPE_POLYGON = 'polygon'

PG_NULL = '__null'

USER_CONFIG_DIR = appdirs.user_config_dir('cartoframes')


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
    return indict.items()


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

    for snake_key in list(snake_keys):
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


def get_geodataframe_data(data, encode_data=True):
    filtered_geometries = _filter_null_geometries(data)
    data = _set_time_cols_epoc(filtered_geometries).to_json(cls=CustomJSONEncoder, separators=(',', ':'))

    if (encode_data):
        compressed_data = gzip.compress(data.encode('utf-8'))
        return base64.b64encode(compressed_data).decode('utf-8')
    else:
        return data


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


def is_valid_str(value):
    return isinstance(value, str) and value != ''


def is_url(text):
    return re.match(r'^https?://.*$', text)


def is_json_filepath(text):
    return re.match(r'^.*\.json\s*$', text, re.IGNORECASE)


def is_uuid(text):
    if text is not None:
        return re.match(r'^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$', text)


def get_credentials(credentials=None):
    from ..auth import defaults
    _credentials = credentials or defaults.get_default_credentials()
    check_credentials(_credentials)
    return _credentials


def check_credentials(credentials):
    from ..auth.credentials import Credentials
    if not isinstance(credentials, Credentials):
        raise ValueError('Credentials attribute is required. '
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
    if isinstance(row, str) and any(key in row for key in special_keys):
        # If the input contains any special key:
        # - replace " by ""
        # - cover the row with "..."
        row = '"{}"'.format(row.replace('"', '""'))

    return '{}'.format(row).encode('utf-8')


def create_hash(value):
    return hashlib.md5(str(value).encode()).hexdigest()


def extract_viz_columns(viz):
    """Extract columns prop('name') in viz"""
    columns = []
    viz_nocomments = remove_comments(viz)
    viz_columns = re.findall(r'prop\([\'\"]([^\)]*)[\'\"]\)', viz_nocomments)
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


def get_local_time():
    local_time = datetime.now(timezone.utc).astimezone()
    return local_time.isoformat()


def timelogger(method):
    def fn(*args, **kw):
        start = time.time()
        result = method(*args, **kw)
        log.debug('%s in %s s', method.__name__, round(time.time() - start, 2))
        return result
    return fn


def check_package(pkg_name, spec='*', is_optional=False):
    try:
        spec_pattern = semantic_version.SimpleSpec(spec)
        pkg_version = pkg_resources.get_distribution(pkg_name).version
        version = semantic_version.Version(pkg_version)
        if not spec_pattern.match(version):
            raise Exception('Package "{0}" version ({1}) does not match "{2}" '.format(pkg_name, version, spec) +
                            'Please run: pip install -U {0}'.format(pkg_name))
    except pkg_resources.DistributionNotFound:
        if is_optional:
            raise Exception('Optional package "{0}" is not installed. '.format(pkg_name) +
                            'Please run: pip install {0}'.format(pkg_name))
        else:
            raise Exception('Package "{0}" is not installed. '.format(pkg_name) +
                            'Please run: pip install {0}'.format(pkg_name))


def check_do_enabled(func):
    @wraps(func)
    def wrapper(*args, **kw):
        try:
            return func(*args, **kw)
        except ServerErrorException as e:
            if str(e) == "['The user does not have Data Observatory enabled']":
                raise DOError(
                    'We are sorry, the Data Observatory is not enabled for your account yet. '
                    'Please contact your customer success manager or send an email to '
                    'sales@carto.com to request access to it.')
            else:
                raise e
    return wrapper


def get_datetime_column_names(df):
    column_names = []
    for column in df.columns:
        if is_datetime(df[column]):
            column_names.append(column)

    return column_names


def is_ipython_notebook():
    """
    Detect whether we are in a Jupyter notebook.
    """
    try:
        cfg = get_ipython().config
        if 'IPKernelApp' in cfg:
            return True
        else:
            return False
    except NameError:
        return False


def get_runtime_env():
    if is_ipython_notebook():
        kernel_class = get_ipython().config['IPKernelApp'].get('kernel_class', '')  # noqa: F821
        if kernel_class.startswith('google.colab'):
            return 'google.colab'
        else:
            return 'notebook'
    else:
        return 'cli'


def save_in_config(content, filename=None, filepath=None):
    if filepath is None:
        if not os.path.exists(USER_CONFIG_DIR):
            os.makedirs(USER_CONFIG_DIR)
        filepath = default_config_path(filename)

    with open(filepath, 'w') as f:
        json.dump(content, f)
        return filepath


def read_from_config(filename=None, filepath=None):
    if filepath is None:
        filepath = default_config_path(filename)

    with open(filepath, 'r') as f:
        return json.load(f)


def default_config_path(filename):
    return os.path.join(USER_CONFIG_DIR, filename)


def silent_fail(method):
    def fn(*args, **kw):
        try:
            return method(*args, **kw)
        except Exception:
            pass
    return fn


def get_parameter_from_decorator(parameter_name, decorated_function, *args, **kwargs):
    parameter = None

    try:
        parameter = kwargs[parameter_name]
    except KeyError:
        try:
            parameter_args = inspect.getargspec(decorated_function).args
            if parameter_name in parameter_args:
                parameter_arg_index = parameter_args.index(parameter_name)
                parameter = args[parameter_arg_index]
        except IndexError:
            pass

    return parameter
