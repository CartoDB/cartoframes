import time

from pandas import read_csv
from warnings import warn

from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException, CartoRateLimitException
from carto.sql import SQLClient, BatchSQLClient, CopySQLClient

from ..dataset_info import DatasetInfo
from ... import __version__
from ...auth.defaults import get_default_credentials
from ...utils.logger import log
from ...utils.geom_utils import encode_geometry_ewkb
from ...utils.utils import is_sql_query, check_credentials, encode_row, map_geom_type, PG_NULL
from ...utils.columns import Column, get_dataframe_columns_info, obtain_converters, \
                      date_columns_names, normalize_name

DEFAULT_RETRY_TIMES = 3


class ContextManager:

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

    def copy_to(self, source, schema, limit=None, retry_times=DEFAULT_RETRY_TIMES):
        query = self.compute_query(source, schema)
        columns = self._get_query_columns_info(query)
        copy_query = self._get_copy_query(query, columns, limit)
        return self._copy_to(copy_query, columns, retry_times)

    def copy_from(self, gdf, table_name, if_exists='fail', cartodbfy=True):
        schema = self.get_schema()
        table_name = self.normalize_table_name(table_name)
        columns = get_dataframe_columns_info(gdf)

        if if_exists == 'replace' or not self.has_table(table_name, schema):
            log.debug('Creating table "{}"'.format(table_name))
            self._create_table_from_columns(table_name, columns, schema, cartodbfy)
        elif if_exists == 'fail':
            raise Exception('Table "{schema}.{table_name}" already exists in your CARTO account. '
                            'Please choose a different `table_name` or use '
                            'if_exists="replace" to overwrite it.'.format(
                                table_name=table_name, schema=schema))
        else:  # 'append'
            pass

        self._copy_from(gdf, table_name, columns)
        return table_name

    def create_table_from_query(self, query, table_name, if_exists, cartodbfy=True):
        schema = self.get_schema()
        table_name = self.normalize_table_name(table_name)

        if if_exists == 'replace' or not self.has_table(table_name, schema):
            log.debug('Creating table "{}"'.format(table_name))
            self._create_table_from_query(query, table_name, schema, cartodbfy)
        elif if_exists == 'fail':
            raise Exception('Table "{schema}.{table_name}" already exists in your CARTO account. '
                            'Please choose a different `table_name` or use '
                            'if_exists="replace" to overwrite it.'.format(
                                table_name=table_name, schema=schema))
        else:  # 'append'
            pass

        return table_name

    def has_table(self, table_name, schema=None):
        query = self.compute_query(table_name, schema)
        return self._check_exists(query)

    def delete_table(self, table_name):
        query = _drop_table_query(table_name)
        output = self.execute_query(query)
        return not('notices' in output and 'does not exist' in output['notices'][0])

    def rename_table(self, table_name, new_table_name, if_exists='fail'):
        new_table_name = self.normalize_table_name(new_table_name)

        if table_name == new_table_name:
            raise ValueError('Table names are equal. Please choose a different table name.')

        if not self.has_table(table_name):
            raise Exception('Table "{table_name}" does not exist in your CARTO account.'.format(
                                table_name=table_name))

        if self.has_table(new_table_name):
            if if_exists == 'replace':
                log.debug('Removing table "{}"'.format(new_table_name))
                self.delete_table(new_table_name)
            elif if_exists == 'fail':
                raise Exception('Table "{new_table_name}" already exists in your CARTO account. '
                                'Please choose a different `new_table_name` or use '
                                'if_exists="replace" to overwrite it.'.format(
                                    new_table_name=new_table_name))

        self._rename_table(table_name, new_table_name)
        return new_table_name

    def update_privacy_table(self, table_name, privacy=None):
        DatasetInfo(self.auth_client, table_name).update_privacy(privacy)

    def get_privacy(self, table_name):
        return DatasetInfo(self.auth_client, table_name).privacy

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
        columns = [c.name for c in self._get_query_columns_info(query)]

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

    def _create_table_from_query(self, query, table_name, schema, cartodbfy=True):
        query = 'BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'.format(
            drop=_drop_table_query(table_name),
            create=_create_table_from_query_query(table_name, query),
            cartodbfy=_cartodbfy_query(table_name, schema) if cartodbfy else ''
        )
        self.execute_long_running_query(query)

    def _create_table_from_columns(self, table_name, columns, schema, cartodbfy=True):
        query = 'BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'.format(
            drop=_drop_table_query(table_name),
            create=_create_table_from_columns_query(table_name, columns),
            cartodbfy=_cartodbfy_query(table_name, schema) if cartodbfy else ''
        )
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

    def _get_query_columns_info(self, query):
        query = 'SELECT * FROM ({}) _q LIMIT 0'.format(query)
        table_info = self.execute_query(query)
        return Column.from_sql_api_fields(table_info['fields'])

    def _get_copy_query(self, query, columns, limit):
        query_columns = [
            column.name for column in columns if (column.name != 'the_geom_webmercator')]

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

        converters = obtain_converters(columns)
        parse_dates = date_columns_names(columns)

        df = read_csv(
            raw_result,
            converters=converters,
            parse_dates=parse_dates)

        return df

    def _copy_from(self, dataframe, table_name, columns):
        query = """
            COPY {table_name}({columns}) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '{null}');
        """.format(
            table_name=table_name, null=PG_NULL,
            columns=','.join(column.dbname for column in columns)).strip()
        data = _compute_copy_data(dataframe, columns)
        self.copy_client.copyfrom(query, data)

    def _rename_table(self, table_name, new_table_name):
        query = _rename_table_query(table_name, new_table_name)
        self.execute_query(query)

    def normalize_table_name(self, table_name):
        norm_table_name = normalize_name(table_name)
        if norm_table_name != table_name:
            log.debug('Table name normalized: "{}"'.format(norm_table_name))
        return norm_table_name


def _drop_table_query(table_name, if_exists=True):
    return '''DROP TABLE {if_exists} {table_name}'''.format(
        table_name=table_name,
        if_exists='IF EXISTS' if if_exists else '')


def _create_table_from_columns_query(table_name, columns):
    columns = ['{name} {type}'.format(name=column.dbname, type=column.dbtype) for column in columns]

    return 'CREATE TABLE {table_name} ({columns})'.format(
        table_name=table_name,
        columns=', '.join(columns))


def _create_table_from_query_query(table_name, query):
    return 'CREATE TABLE {table_name} AS ({query})'.format(table_name=table_name, query=query)


def _cartodbfy_query(table_name, schema):
    return "SELECT CDB_CartodbfyTable('{schema}', '{table_name}')" \
        .format(schema=schema, table_name=table_name)


def _rename_table_query(table_name, new_table_name):
    return 'ALTER TABLE {table_name} RENAME TO {new_table_name};'.format(
        table_name=table_name, new_table_name=new_table_name)


def _create_auth_client(credentials, public=False):
    return APIKeyAuthClient(
        base_url=credentials.base_url,
        api_key='default_public' if public else credentials.api_key,
        session=credentials.session,
        client_id='cartoframes_{}'.format(__version__),
        user_agent='cartoframes_{}'.format(__version__)
    )


def _compute_copy_data(df, columns):
    for index, _ in df.iterrows():
        row_data = []
        for column in columns:
            val = df.at[index, column.name]

            if column.is_geom:
                val = encode_geometry_ewkb(val)

            row_data.append(encode_row(val))

        csv_row = b'|'.join(row_data)
        csv_row += b'\n'

        yield csv_row
