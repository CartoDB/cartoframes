"""Functions to interact with the CARTO platform"""

import pandas as pd

from ..core.cartodataframe import CartoDataFrame
from ..auth.defaults import get_default_credentials
from ..lib.context import create_context
from ..utils.utils import is_sql_query, check_credentials, PG_NULL
from ..utils.geom_utils import compute_query_from_table
from ..utils.columns import Column, obtain_index_col, obtain_converters, date_columns_names


def read_carto(source, credentials=None, limit=None, retry_times=3, schema=None,
               keep_cartodb_id=False, keep_the_geom=False, keep_the_geom_webmercator=False):
    """
    Read a table or a SQL query from a CARTO account.

    Args:
        source (str): table name or SQL query.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        limit (int, optional):
            The number of rows to download. Default is to download all rows.
        retry_times (int, optional):
            Number of time to retry the download in case it fails. Default is 3.
        keep_cartodb_id (bool, optional): retrieve the "cartodb_id" column.
        keep_the_geom (bool, optional): retrieve the "the_geom" column.
        schema (str, optional):

    Returns:
        :py:class:`CartoDataFrame <cartoframes.core.CartoDataFrame>`

    """
    _check_source(source)

    credentials = credentials or get_default_credentials()
    check_credentials(credentials)

    context = create_context(credentials)

    query = _compute_query(source, schema, context)

    _check_exists(query, context)

    columns = _get_query_columns(query, context)

    copy_query = _get_copy_query(query, columns, limit, keep_the_geom_webmercator)

    df = _copyto(copy_query, columns, retry_times, context)

    return CartoDataFrame(
        df,
        index_column='cartodb_id',
        geom_column='the_geom',
        keep_index=keep_cartodb_id,
        keep_geom=keep_the_geom
    )


def _check_source(source):
    if not isinstance(source, str):
        raise ValueError('Wrong source. You should provide a valid table_name or SQL query.')


def _compute_query(source, schema, context):
    if is_sql_query(source):
        print('Debug: SQL query detected')
        return source
    print('Debug: table name detected')
    schema = schema or context.get_schema()
    return compute_query_from_table(source, schema)


def _check_exists(query, context):
    exists, msg = context.exists(query)
    if not exists:
        raise ValueError(msg)


def _get_query_columns(query, context):
    query = 'SELECT * FROM ({}) _q LIMIT 0'.format(query)
    table_info = context.execute_query(query)
    return Column.from_sql_api_fields(table_info['fields'])


def _get_copy_query(query, columns, limit=None, keep_the_geom_webmercator=False):
    query_columns = [
        column.name for column in columns if (column.name != 'the_geom_webmercator'
                                              or keep_the_geom_webmercator)]

    query = 'SELECT {columns} FROM ({query}) _q'.format(
        query=query,
        columns=','.join(query_columns))

    if limit is not None:
        if isinstance(limit, int) and (limit >= 0):
            query += ' LIMIT {limit}'.format(limit=limit)
        else:
            raise ValueError("`limit` parameter must an integer >= 0")

    return query


def _copyto(query, columns, retry_times, context):
    copy_query = 'COPY ({0}) TO stdout WITH (FORMAT csv, HEADER true, NULL \'{1}\')'.format(query, PG_NULL)
    raw_result = context.download(copy_query, retry_times)

    index_col = obtain_index_col(columns)
    converters = obtain_converters(columns, decode_geom=True)
    parse_dates = date_columns_names(columns)

    df = pd.read_csv(
        raw_result,
        converters=converters,
        parse_dates=parse_dates)

    if index_col:
        df.index = df[index_col]
        df.index.name = None

    return df


def to_carto():
    pass
