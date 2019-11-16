"""Functions to interact with the CARTO platform"""

import pandas as pd

from ..core.cartodataframe import CartoDataFrame
from ..auth.defaults import get_default_credentials
from ..lib.context import create_context
from ..utils.utils import is_sql_query, check_credentials, encode_row, PG_NULL
from ..utils.geom_utils import compute_query_from_table, decode_geometry
from ..utils.columns import Column, DataframeColumnsInfo, obtain_index_col, \
                            obtain_converters, date_columns_names, normalize_name


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
    _check_dataframe(dataframe)
    _check_table_name(table_name)

    norm_table_name = normalize_name(table_name)
    if norm_table_name != table_name:
        print('Debug: table name normalized: "{}"'.format(norm_table_name))

    credentials = credentials or get_default_credentials()
    check_credentials(credentials)

    context = create_context(credentials)

    cdf = CartoDataFrame(dataframe, copy=True)

    dataframe_columns_info = DataframeColumnsInfo(cdf)

    schema = context.get_schema()

    if if_exists == 'replace' or not _has_table(norm_table_name, schema, context):
        print('Debug: creating table')
        _create_table(norm_table_name, dataframe_columns_info.columns, schema, context)
    elif if_exists == 'fail':
        raise Exception('Table "{schema}.{table_name}" already exists in CARTO. '
                        'Please choose a different `table_name` or use '
                        'if_exists="replace" to overwrite it'.format(
                            table_name=norm_table_name, schema=schema))
    elif if_exists == 'append':
        pass

    _copyfrom(cdf, norm_table_name, dataframe_columns_info, context)
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

    _check_table_name(table_name)

    credentials = credentials or get_default_credentials()
    check_credentials(credentials)

    context = create_context(credentials)

    schema = context.get_schema()

    return _has_table(table_name, schema, context)


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


def _has_table(table, schema, context):
    try:
        query = compute_query_from_table(table, schema)
        _check_exists(query, context)
        return True
    except Exception:
        return False


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


def _check_dataframe(dataframe):
    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError('Wrong dataframe. You should provide a valid DataFrame instance.')


def _check_table_name(table_name):
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')


def _create_table(table_name, columns, schema, context):
    query = '''BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'''.format(
        drop=_drop_table_query(table_name),
        create=_create_table_query(table_name, columns),
        cartodbfy=_cartodbfy_query(table_name, schema))

    context.execute_long_running_query(query)


def _drop_table_query(table_name, if_exists=True):
    return '''DROP TABLE {if_exists} {table_name}'''.format(
        table_name=table_name,
        if_exists='IF EXISTS' if if_exists else '')


def _create_table_query(table_name, columns):
    cols = ['{column} {type}'.format(column=c.database, type=c.database_type) for c in columns]

    return '''CREATE TABLE {table_name} ({cols})'''.format(
        table_name=table_name,
        cols=', '.join(cols))


def _cartodbfy_query(table_name, schema):
    return "SELECT CDB_CartodbfyTable('{schema}', '{table_name}')" \
        .format(schema=schema, table_name=table_name)


def _copyfrom(dataframe, table_name, dataframe_columns_info, context):
    query = """
        COPY {table_name}({columns}) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '{null}');
    """.format(
        table_name=table_name, null=PG_NULL,
        columns=','.join(c.database for c in dataframe_columns_info.columns)).strip()

    data = _rows(dataframe, dataframe_columns_info)

    context.upload(query, data)


def _rows(df, dataframe_columns_info):
    for index, _ in df.iterrows():
        row_data = []
        for c in dataframe_columns_info.columns:
            col = c.dataframe
            if col not in df.columns:
                if df.index.name and col == df.index.name:
                    val = index
                else:  # we could have filtered columns in the df. See DataframeColumnsInfo
                    continue
            else:
                val = df.at[index, col]

            if dataframe_columns_info.geom_column and col == dataframe_columns_info.geom_column:
                geom = decode_geometry(val, dataframe_columns_info.enc_type)
                if geom:
                    val = 'SRID=4326;{}'.format(geom.wkt)
                else:
                    val = ''

            row_data.append(encode_row(val))

        csv_row = b'|'.join(row_data)
        csv_row += b'\n'

        yield csv_row
