"""Functions to interact with the CARTO platform"""

import pandas as pd

from ..cartodataframe import CartoDataFrame
from ..auth.defaults import get_default_credentials
from ..lib.context import create_context
from ..utils.utils import is_sql_query, check_credentials, PG_NULL
from ..utils.geom_utils import compute_query_from_table, geodataframe_from_dataframe
from ..utils.columns import Column, normalize_name, obtain_index_col, obtain_converters, date_columns_names


def read_carto(source, credentials=None, limit=None, retry_times=3,
               keep_cartodb_id=False, keep_the_geom=False, schema=None):
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
        :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`

    """
    _check_source(source)

    credentials = credentials or get_default_credentials()
    check_credentials(credentials)

    context = create_context(credentials)
    schema = schema or context.get_schema()

    query = _compute_query(source, schema)

    columns = _get_query_columns(query, context)

    copy_query = _get_copy_query(query, columns, limit)

    df = _copyto(columns, copy_query, limit, retry_times, context)
    df.index.name = None

    gdf = geodataframe_from_dataframe(df)

    if keep_cartodb_id:
        gdf['cartodb_id'] = gdf.index

    if not keep_the_geom:
        del gdf['the_geom']

    return CartoDataFrame(gdf)


def _check_source(source):
    if not isinstance(source, str):
        raise ValueError('Wrong source. You should provide a valid table_name or SQL query.')


def _compute_query(source, schema):
    if is_sql_query(source):
        print('Debug: SQL query detected')
        return source
    print('Debug: table name detected')
    table_name = normalize_name(source)
    if table_name != source:
        print('Debug: table name normalized: {}'.format(table_name))
    return compute_query_from_table(table_name, schema)


def _get_query_columns(query, context):
    query = 'SELECT * FROM ({}) _q LIMIT 0'.format(query)
    table_info = context.execute_query(query)
    return Column.from_sql_api_fields(table_info['fields'])


def _get_copy_query(query, columns, limit=None):
    query_columns = [column.name for column in columns if column.name != 'the_geom_webmercator']

    query = 'SELECT {columns} FROM ({query}) _q'.format(
        query=query,
        columns=', '.join(query_columns))

    if limit is not None:
        if isinstance(limit, int) and (limit >= 0):
            query += ' LIMIT {limit}'.format(limit=limit)
        else:
            raise ValueError("`limit` parameter must an integer >= 0")

    return query


def _copyto(columns, query, limit, retry_times, context):
    copy_query = 'COPY ({0}) TO stdout WITH (FORMAT csv, HEADER true, NULL \'{1}\')'.format(query, PG_NULL)
    raw_result = context.download(copy_query, retry_times)

    index_col = obtain_index_col(columns)
    converters = obtain_converters(columns, decode_geom=True)
    parse_dates = date_columns_names(columns)

    df = pd.read_csv(
        raw_result,
        index_col=index_col,
        converters=converters,
        parse_dates=parse_dates)

    return df


def to_carto():
    pass
