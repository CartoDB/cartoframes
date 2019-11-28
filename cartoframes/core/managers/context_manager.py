import time
import pandas as pd

from warnings import warn

from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException, CartoRateLimitException
from carto.sql import SQLClient, BatchSQLClient, CopySQLClient

from ...io.dataset_info import DatasetInfo

from ...auth.defaults import get_default_credentials

from ...utils.geom_utils import decode_geometry
from ...utils.utils import is_sql_query, check_credentials, encode_row, map_geom_type, PG_NULL
from ...utils.columns import Column, DataframeColumnsInfo, obtain_index_col, obtain_converters, \
                            date_columns_names, normalize_name

from ... import __version__

DEFAULT_RETRY_TIMES = 3

# TODO: refactor


class ContextManager(object):

    def __init__(self, credentials):
        self.credentials = credentials or get_default_credentials()
        check_credentials(self.credentials)

        self.auth_client = _create_auth_client(self.credentials)
        self.sql_client = SQLClient(self.auth_client)
        self.copy_client = CopySQLClient(self.auth_client)
        self.batch_sql_client = BatchSQLClient(self.auth_client)

    def execute_query(self, query, parse_json=True, do_post=True, format=None, **request_args):
        return self.sql_client.send(query.strip(), parse_json, do_post, format, **request_args)

    def execute_long_running_query(self, query):
        return self.batch_sql_client.create_and_wait_for_completion(query.strip())

    def copy_to(self, source, schema, limit=None, retry_times=DEFAULT_RETRY_TIMES, drop_the_geom_webmercator=False):
        query = self.compute_query(source, schema)
        columns = self._get_columns(query)
        copy_query = self._get_copy_query(query, columns, limit, drop_the_geom_webmercator)
        return self._copy_to(copy_query, columns, retry_times)

    def copy_from(self, cdf, table_name, if_exists, log_enabled=True):
        dataframe_columns_info = DataframeColumnsInfo(cdf)
        schema = self.get_schema()
        table_name = self.normalize_table_name(table_name)

        if if_exists == 'replace' or not self.has_table(table_name, schema):
            if log_enabled:
                print('Debug: creating table "{}"'.format(table_name))
            self._create_table_from_columns(table_name, dataframe_columns_info.columns, schema)
        elif if_exists == 'fail':
            raise Exception('Table "{schema}.{table_name}" already exists in CARTO. '
                            'Please choose a different `table_name` or use '
                            'if_exists="replace" to overwrite it'.format(
                                table_name=table_name, schema=schema))

        return self._copy_from(cdf, table_name, dataframe_columns_info)

    def create_table_from_query(self, table_name, query, if_exists, log_enabled=True):
        schema = self.get_schema()
        table_name = self.normalize_table_name(table_name)

        if if_exists == 'replace' or not self.has_table(table_name, schema):
            if log_enabled:
                print('Debug: creating table "{}"'.format(table_name))
            self._create_table_from_query(table_name, query, schema)
        elif if_exists == 'fail':
            raise Exception('Table "{schema}.{table_name}" already exists in CARTO. '
                            'Please choose a different `table_name` or use '
                            'if_exists="replace" to overwrite it'.format(
                                table_name=table_name, schema=schema))

    def has_table(self, table_name, schema=None):
        query = self.compute_query(table_name, schema)
        return self._check_exists(query)

    def delete_table(self, table_name):
        query = _drop_table_query(table_name)
        output = self.execute_query(query)
        if ('does not exist' in output['notices'][0]):
            print('Debug: table "{}" does not exist'.format(table_name))
        else:
            print('Debug: table "{}" removed'.format(table_name))

    def update_table(self, table_name, privacy=None, new_table_name=None):
        dataset_info = DatasetInfo(self.auth_client, table_name)
        dataset_info.update(privacy, new_table_name)

    def get_privacy(self, table_name):
        dataset_info = DatasetInfo(self.auth_client, table_name)
        return dataset_info.privacy

    def get_schema(self):
        """Get user schema from current credentials"""
        query = 'SELECT current_schema()'
        result = self.execute_query(query, do_post=False)
        return result['rows'][0]['current_schema']

    def get_geom_type(self, query):
        """Fetch geom type of a remote table or query"""
        distict_query = '''
            SELECT distinct ST_GeometryType(the_geom) AS geom_type
            FROM ({}) q
            LIMIT 5
        '''.format(query)
        response = self.execute_query(distict_query, do_post=False)
        if response and response.get('rows') and len(response.get('rows')) > 0:
            st_geom_type = response.get('rows')[0].get('geom_type')
            if st_geom_type:
                return map_geom_type(st_geom_type[3:])
        return None

    def get_num_rows(self, query):
        """Get the number of rows in the query"""
        result = self.execute_query("SELECT COUNT(*) FROM ({query}) _query".format(query=query))
        return result.get('rows')[0].get('count')

    def get_bounds(self, query):
        extent_query = '''
            SELECT ARRAY[
                ARRAY[st_xmin(geom_env), st_ymin(geom_env)],
                ARRAY[st_xmax(geom_env), st_ymax(geom_env)]
            ] bounds FROM (
                SELECT ST_Extent(the_geom) geom_env
                FROM ({}) q
            ) q;
        '''.format(query)
        response = self.execute_query(extent_query, do_post=False)
        if response and response.get('rows') and len(response.get('rows')) > 0:
            return response.get('rows')[0].get('bounds')
        return None

    def get_column_names(self, source, schema=None, exclude=None):
        query = self.compute_query(source, schema)
        columns = [c.name for c in self._get_columns(query)]

        if exclude and isinstance(exclude, list):
            columns = list(set(columns) - set(exclude))

        return columns

    def is_public(self, query):
        # Used to detect public tables in queries in the publication,
        # because privacy only works for tables.
        public_auth_client = _create_auth_client(self.credentials, public=True)
        public_sql_client = SQLClient(public_auth_client)
        exists_query = 'EXPLAIN {}'.format(query)
        try:
            public_sql_client.send(exists_query, do_post=False)
            return True
        except CartoException:
            return False

    def get_table_names(self, query):
        # Used to detect tables in queries in the publication.
        query = 'SELECT CDB_QueryTablesText(\'{}\') as tables'.format(query)
        result = self.execute_query(query)
        tables = []
        if result['total_rows'] > 0 and result['rows'][0]['tables']:
            # Dataset_info only works with tables without schema
            tables = [table.split('.')[1] if '.' in table else table for table in result['rows'][0]['tables']]
        return tables

    def _create_table_from_query(self, table_name, query, schema):
        query = 'BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'.format(
            drop=_drop_table_query(table_name),
            create=_create_table_from_query_query(table_name, query),
            cartodbfy=_cartodbfy_query(table_name, schema))
        self.execute_long_running_query(query)

    def _create_table_from_columns(self, table_name, columns, schema):
        query = 'BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'.format(
            drop=_drop_table_query(table_name),
            create=_create_table_from_columns_query(table_name, columns),
            cartodbfy=_cartodbfy_query(table_name, schema))
        self.execute_long_running_query(query)

    def compute_query(self, source, schema=None):
        if is_sql_query(source):
            return source
        schema = schema or self.get_schema()
        return self._compute_query_from_table(source, schema)

    def _compute_query_from_table(self, table_name, schema):
        return 'SELECT * FROM "{schema}"."{table_name}"'.format(
            schema=schema or 'public',
            table_name=table_name
        )

    def _check_exists(self, query):
        exists_query = 'EXPLAIN {}'.format(query)
        try:
            self.execute_query(exists_query, do_post=False)
            return True
        except CartoException:
            return False

    def _get_columns(self, query):
        query = 'SELECT * FROM ({}) _q LIMIT 0'.format(query)
        table_info = self.execute_query(query)
        return Column.from_sql_api_fields(table_info['fields'])

    def _get_copy_query(self, query, columns, limit, drop_the_geom_webmercator):
        query_columns = [
            column.name for column in columns if (column.name != 'the_geom_webmercator'
                                                  or not drop_the_geom_webmercator)]

        query = 'SELECT {columns} FROM ({query}) _q'.format(
            query=query,
            columns=','.join(query_columns))

        if limit is not None:
            if isinstance(limit, int) and (limit >= 0):
                query += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")

        return query

    def _copy_to(self, query, columns, retry_times):
        copy_query = 'COPY ({0}) TO stdout WITH (FORMAT csv, HEADER true, NULL \'{1}\')'.format(query, PG_NULL)

        try:
            raw_result = self.copy_client.copyto_stream(copy_query)
        except CartoRateLimitException as err:
            if retry_times > 0:
                retry_times -= 1
                warn('Read call rate limited. Waiting {s} seconds'.format(s=err.retry_after))
                time.sleep(err.retry_after)
                warn('Retrying...')
                return self._copy_to(query, columns, retry_times)
            else:
                warn(('Read call was rate-limited. '
                      'This usually happens when there are multiple queries being read at the same time.'))
                raise err

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

    def _copy_from(self, dataframe, table_name, dataframe_columns_info):
        query = """
            COPY {table_name}({columns}) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '{null}');
        """.format(
            table_name=table_name, null=PG_NULL,
            columns=','.join(c.database for c in dataframe_columns_info.columns)).strip()

        data = _rows(dataframe, dataframe_columns_info)

        self.copy_client.copyfrom(query.strip(), data)

    def normalize_table_name(self, table_name):
        norm_table_name = normalize_name(table_name)
        if norm_table_name != table_name:
            print('Debug: table name normalized: "{}"'.format(norm_table_name))
        return norm_table_name


def _drop_table_query(table_name, if_exists=True):
    return '''DROP TABLE {if_exists} {table_name}'''.format(
        table_name=table_name,
        if_exists='IF EXISTS' if if_exists else '')


def _create_table_from_columns_query(table_name, columns):
    cols = ['{column} {type}'.format(column=c.database, type=c.database_type) for c in columns]

    return 'CREATE TABLE {table_name} ({cols})'.format(
        table_name=table_name,
        cols=', '.join(cols))


def _create_table_from_query_query(table_name, query):
    return 'CREATE TABLE {table_name} AS ({query})'.format(table_name=table_name, query=query)


def _cartodbfy_query(table_name, schema):
    return "SELECT CDB_CartodbfyTable('{schema}', '{table_name}')" \
        .format(schema=schema, table_name=table_name)


def _create_auth_client(credentials, public=False):
    return APIKeyAuthClient(
        base_url=credentials.base_url,
        api_key='default_public' if public else credentials.api_key,
        session=credentials.session,
        client_id='cartoframes_{}'.format(__version__),
        user_agent='cartoframes_{}'.format(__version__)
    )


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


# def _rename_index_for_upload(self):
#     if self._df.index.name != 'cartodb_id':
#         if 'cartodb_id' not in self._df:
#             if _is_valid_index_for_cartodb_id(self._df.index):
#                 # rename a integer unnamed index to cartodb_id
#                 self._df.index.rename('cartodb_id', inplace=True)
#         else:
#             if self._df.index.name is None:
#                 # replace an unnamed index by a cartodb_id column
#                 self._df.set_index('cartodb_id')


# def _is_valid_index_for_cartodb_id(index):
#     return index.name is None and index.nlevels == 1 and index.dtype == 'int' and index.is_unique
