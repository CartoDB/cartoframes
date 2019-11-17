"""Functions to interact with the CARTO platform"""

import pandas as pd

from .context import ContextManager

from ..core.cartodataframe import CartoDataFrame


def read_carto(source, credentials=None, limit=None, retry_times=3, schema=None,
               keep_cartodb_id=False, keep_the_geom=False, keep_the_geom_webmercator=False):
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
        schema (str, optional):prefix of the table. By default, it gets the
            `current_schema()` using the credentials.
        keep_cartodb_id (bool, optional): retrieve the "cartodb_id" column.
        keep_the_geom (bool, optional): retrieve the "the_geom" column.
        keep_the_goem_webmercator (bool, optional): retrieve the "the_geom_webmercator" column.

    Returns:
        :py:class:`CartoDataFrame <cartoframes.core.CartoDataFrame>`

    """
    if not isinstance(source, str):
        raise ValueError('Wrong source. You should provide a valid table_name or SQL query.')

    manager = ContextManager(credentials)

    df = manager.copy_to(source, schema, limit, retry_times, keep_the_geom_webmercator)

    return CartoDataFrame(
        df,
        index_column='cartodb_id',
        geom_column='the_geom',
        keep_index=keep_cartodb_id,
        keep_geom=keep_the_geom
    )


def to_carto(dataframe, table_name, credentials=None, if_exists='fail'):
    """
    Read a table or a SQL query from the CARTO account.

    Args:
        dataframe (DataFrame): data frame to upload.
        table_name (str): name of the table to upload the data.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace', 'append'. Default is 'fail'.

    """
    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError('Wrong dataframe. You should provide a valid DataFrame instance.')

    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    manager = ContextManager(credentials)

    cdf = CartoDataFrame(dataframe, copy=True)

    manager.copy_from(cdf, table_name, if_exists)

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

    manager = ContextManager(credentials)

    return manager.has_table(table_name, schema)


def delete_table(table_name, credentials=None):
    """
    Delete the table from the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    manager = ContextManager(credentials)

    return manager.delete_table(table_name)


def describe_table(table_name, credentials=None):
    """
    Describe the table in the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    manager = ContextManager(credentials)

    return {
        'privacy': manager.get_privacy(table_name),
        'num_rows': manager.get_num_rows(table_name),
        'geom_type': manager.get_geom_type(table_name)
    }


def update_table(table_name, credentials=None, privacy=None, new_table_name=None):
    """
    Update the table information in the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        privacy (str, optional): privacy of the table: 'PRIVATE', 'PUBLIC', 'LINK'.
        new_table_name(str, optional): new name for the table.
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    valid_privacy_values = ['PRIVATE', 'PUBLIC', 'LINK']
    if privacy not in valid_privacy_values:
        raise ValueError('Wrong privacy. Valid names are {}'.format(', '.join(valid_privacy_values)))

    manager = ContextManager(credentials)
    manager.update_table(table_name, privacy, new_table_name)
