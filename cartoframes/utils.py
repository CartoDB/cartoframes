import sys
from tqdm import tqdm
from functools import wraps
from warnings import filterwarnings, catch_warnings


def dict_items(d):
    if sys.version_info >= (3, 0):
        return d.items()
    else:
        return d.iteritems()


def cssify(css_dict):
    css = ''
    for key, value in dict_items(css_dict):
        css += '{key} {{ '.format(key=key)
        for field, field_value in dict_items(value):
            css += ' {field}: {field_value};'.format(field=field,
                                                     field_value=field_value)
        css += '} '
    return css.strip()


def normalize_colnames(columns):
    """SQL-normalize columns in `dataframe` to reflect changes made through
    CARTO's SQL API.

    Args:
        columns (list of str): List of column names

    Returns:
        list of str: Normalized column names
    """
    normalized_columns = [norm_colname(c) for c in columns]
    changed_cols = '\n'.join([
        '\033[1m{orig}\033[0m -> \033[1m{new}\033[0m'.format(
            orig=c,
            new=normalized_columns[i])
        for i, c in enumerate(columns)
        if c != normalized_columns[i]])
    if changed_cols != '':
        tqdm.write('The following columns were changed in the CARTO '
                   'copy of this dataframe:\n{0}'.format(changed_cols))

    return normalized_columns


def norm_colname(colname):
    """Given an arbitrary column name, translate to a SQL-normalized column
    name a la CARTO's Import API will translate to

    Examples
        * 'Field: 2' -> 'field_2'
        * '2 Items' -> '_2_items'

    Args:
        colname (str): Column name that will be SQL normalized
    Returns:
        str: SQL-normalized column name
    """
    last_char_special = False
    char_list = []
    for e in str(colname):
        if e.isalnum():
            char_list.append(e.lower())
            last_char_special = False
        else:
            if not last_char_special:
                char_list.append('_')
                last_char_special = True
            else:
                last_char_special = False
    final_name = ''.join(char_list)
    if final_name[0].isdigit():
        return '_' + final_name
    return final_name


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
