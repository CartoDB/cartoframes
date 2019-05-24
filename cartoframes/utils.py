"""general utility functions"""

import re
import sys
import hashlib

from functools import wraps
from warnings import filterwarnings, catch_warnings


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
