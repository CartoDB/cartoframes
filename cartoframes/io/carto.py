"""Functions to interact with the CARTO platform"""

from __future__ import absolute_import

import pandas as pd

from carto.exceptions import CartoException

from ..core.cartodataframe import CartoDataFrame
from ..core.managers.context_manager import ContextManager
from ..utils.utils import is_sql_query


GEOM_COLUMN_NAME = 'the_geom'


def read_carto(source, credentials=None, limit=None, retry_times=3, schema=None, index_col=None, decode_geom=True):
    """
    Read a table or a SQL query from the CARTO account.

    Args:
        source (str): table name or SQL query.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        limit (int, optional):
            The number of rows to download. Default is to download all rows.
        retry_times (int, optional):
            Number of time to retry the download in case it fails. Default is 3.
        schema (str, optional): prefix of the table. By default, it gets the
            `current_schema()` using the credentials.
        index_col (str, optional): name of the column to be loaded as index. It can be used also to set the index name.
        decode_geom (bool, optional): convert the "the_geom" column into a valid geometry column.

    Returns:
        :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`

    """
    if not isinstance(source, str):
        raise ValueError('Wrong source. You should provide a valid table_name or SQL query.')

    context_manager = ContextManager(credentials)

    df = context_manager.copy_to(source, schema, limit, retry_times)

    cdf = CartoDataFrame(df, crs='epsg:4326')

    if index_col:
        if index_col in cdf:
            cdf.set_index(index_col, inplace=True)
        else:
            cdf.index.name = index_col

    if decode_geom and GEOM_COLUMN_NAME in cdf:
        # Decode geometry column
        cdf.set_geometry(GEOM_COLUMN_NAME, inplace=True)

    return cdf


def to_carto(dataframe, table_name, credentials=None, if_exists='fail', geom_col=None, index=False, index_label=None,
             log_enabled=True, force_cartodbfy=False):
    """
    Upload a Dataframe to CARTO.

    Args:
        dataframe (DataFrame, GeoDataFrame, :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`):
            data to be uploaded.
        table_name (str): name of the table to upload the data.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace', 'append'. Default is 'fail'.
        geom_col (str, optional): name of the geometry column of the dataframe.
        index (bool, optional): write the index in the table. Default is False.
        index_label (str, optional): name of the index column in the table. By default it
            uses the name of the index from the dataframe.

    """
    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError('Wrong dataframe. You should provide a valid DataFrame instance.')

    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)

    cdf = CartoDataFrame(dataframe, copy=True)

    if index:
        index_name = index_label or cdf.index.name
        if index_name is not None and index_name != '':
            # Append the index as a column
            cdf[index_name] = cdf.index
        else:
            raise ValueError('Wrong index name. You should provide a valid index label.')

    if geom_col in cdf:
        # Decode geometry column
        cdf.set_geometry(geom_col, inplace=True)

    has_geometry = cdf.has_geometry()
    if has_geometry:
        # Prepare geometry column for the upload
        cdf.rename_geometry(GEOM_COLUMN_NAME, inplace=True)

    cartodbfy = force_cartodbfy or has_geometry

    context_manager.copy_from(cdf, table_name, if_exists, cartodbfy, log_enabled)

    if log_enabled:
        print('Success! Data uploaded correctly')


def has_table(table_name, credentials=None, schema=None):
    """
    Check if the table exists in the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        schema (str, optional):prefix of the table. By default, it gets the
            `current_schema()` using the credentials.
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)

    return context_manager.has_table(table_name, schema)


def delete_table(table_name, credentials=None, log_enabled=True):
    """
    Delete the table from the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)

    return context_manager.delete_table(table_name, log_enabled)


def describe_table(table_name, credentials=None, schema=None):
    """
    Describe the table in the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        schema (str, optional):prefix of the table. By default, it gets the
            `current_schema()` using the credentials.

    Returns:
        A dict with the `privacy`, `num_rows` and `geom_type` of the table.

    Raises:
        ValueError:
            If the table name is not a string.
    """

    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)
    query = context_manager.compute_query(table_name, schema)

    try:
        privacy = context_manager.get_privacy(table_name)
    except CartoException:
        # There is an issue with ghost tables when
        # the table is created for the first time
        print('Debug: we can not retrieve the privacy from the metadata')
        privacy = ''

    return {
        'privacy': privacy,
        'num_rows': context_manager.get_num_rows(query),
        'geom_type': context_manager.get_geom_type(query)
    }


def update_table(table_name, credentials=None, new_table_name=None, privacy=None, log_enabled=True):
    """
    Update the table information in the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        new_table_name(str, optional): new name for the table.
        privacy (str, optional): privacy of the table: 'private', 'public', 'link'.

    Raises:
        ValueError:
            If the table name is not a string.
        ValueError:
            If the privacy name is not 'private', 'public', or 'link'.
    """

    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    valid_privacy_values = ['PRIVATE', 'PUBLIC', 'LINK']
    if privacy.upper() not in valid_privacy_values:
        raise ValueError('Wrong privacy. Valid names are {}'.format(', '.join(valid_privacy_values)))

    context_manager = ContextManager(credentials)
    context_manager.update_table(table_name, privacy, new_table_name)

    if log_enabled:
        print('Success! Table updated correctly')


def copy_table(table_name, new_table_name, credentials=None, if_exists='fail', log_enabled=True):
    """
    Copy a table into a new table in the CARTO account.

    Args:
        table_name (str): name of the original table.
        new_table_name(str, optional): name for the new table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace'. Default is 'fail'.
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid string.')

    if not isinstance(new_table_name, str):
        raise ValueError('Wrong new table name. You should provide a valid string.')
    pass

    context_manager = ContextManager(credentials)

    query = 'SELECT * FROM {}'.format(table_name)
    context_manager.create_table_from_query(new_table_name, query, if_exists)

    if log_enabled:
        print('Success! Table copied correctly')


def create_table_from_query(query, new_table_name, credentials=None, if_exists='fail', log_enabled=True):
    """
    Create a new table from an SQL query in the CARTO account.

    Args:
        query (str): SQL query
        new_table_name(str): name for the new table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace'. Default is 'fail'.
    """
    if not is_sql_query(query):
        raise ValueError('Wrong query. You should provide a valid SQL query.')

    if not isinstance(new_table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')
    pass

    context_manager = ContextManager(credentials)

    context_manager.create_table_from_query(new_table_name, query, if_exists)

    if log_enabled:
        print('Success! Table created correctly')
