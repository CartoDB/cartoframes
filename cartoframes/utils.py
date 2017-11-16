import sys
from tqdm import tqdm


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
    return css


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


def importify_params(param_arg):
    """Convert parameter arguments to what CARTO's Import API expects"""
    if isinstance(param_arg, bool):
        return str(param_arg).lower()
    return param_arg


def join_url(*parts):
    """join parts of URL into complete url"""
    return '/'.join(s.strip('/') for s in parts)


def data_obs_country2tag(country):
    """Maps a country name to a Data Observatory tag.
    Country names are pegged to the following query:

    .. code::sql

        SELECT
          count(*) num_measurements,
          tag.key region_id,
          tag.value region_name
        FROM (
          SELECT *
          FROM OBS_GetAvailableNumerators()
          WHERE jsonb_pretty(numer_tags) LIKE '%subsection/%'
        ) numers,
        Jsonb_Each(numers.numer_tags) tag
        WHERE tag.key like 'section%'
        GROUP BY tag.key, tag.value
        ORDER BY region_name
    """
    tags = {
        'Australia': 'section/tags.au',
        'Brazil': 'section/tags.br',
        'Canada': 'section/tags.ca',
        'European Union': 'section/tags.eu',
        'France': 'section/tags.fr',
        'Mexico': 'section/tags.mx',
        'Spain': 'section/tags.spain',
        'United Kingdom': 'section/tags.uk',
        'United States': 'section/tags.united_states'
    }
    norm_name = {
        'Australia': 'Australia',
        'Brazil': 'Brazil',
        'Canada': 'Canada',
        'European Union': 'European Union',
        'France': 'France',
        'Mexico': 'Mexico',
        'Spain': 'Spain',
        'United Kingdom': 'United Kingdom',
        'United States': 'United States',
        'Brasil': 'Brazil',
        'EU': 'European Union',
        'E.U.': 'European Union',
        'México': 'Mexico',
        'Méjico': 'Mexico',
        'Espana': 'Spain',
        'España': 'Spain',
        'UK': 'United Kingdom',
        'U.K.': 'United Kingdom',
        'United States of America': 'United States',
        'USA': 'United States',
        'U.S.': 'United States',
        'U.S.A.': 'United States'
    }
    try:
        return tags.get(norm_name[country])
    except KeyError:
        raise ValueError('`{0}` is not available. The only available '
                         'countries are {1}.'.format(
                             country,
                             ', '.join('\'{}\''.format(k) for k in tags.keys())
                         ))
