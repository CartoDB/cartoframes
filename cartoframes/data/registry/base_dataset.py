from abc import ABCMeta, abstractmethod
import pandas as pd

from carto.exceptions import CartoException, CartoRateLimitException

from ..dataset_info import DatasetInfo
from ..utils import decode_geometry, compute_query, convert_bool, \
    get_context_with_public_creds, ENC_WKB_BHEX
from ... import utils
from ... import context
from ..columns import Column, normalize_name, dtypes, date_columns_names, bool_columns_names


class BaseDataset():
    __metaclass__ = ABCMeta

    FAIL = 'fail'
    REPLACE = 'replace'
    APPEND = 'append'

    def __init__(self, credentials=None):
        self._verbose = 0
        self._credentials = credentials
        self._context = self._create_context()
        self._table_name = None
        self._schema = None
        self._dataset_info = None

    @staticmethod
    @abstractmethod
    def can_work_with():
        pass

    @classmethod
    @abstractmethod
    def create(cls):
        pass

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def upload(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @property
    def credentials(self):
        """Dataset :py:class:`Context <cartoframes.auth.Context>`"""
        return self._credentials

    @credentials.setter
    def credentials(self, credentials):
        """Set a new :py:class:`Context <cartoframes.auth.Context>` for a Dataset instance."""
        self._credentials = credentials
        self._context = self._create_context()
        self._schema = self._get_schema()

    @property
    def table_name(self):
        """Dataset table name"""
        return self._table_name

    @table_name.setter
    def table_name(self, table_name):
        self._table_name = normalize_name(table_name)

    @property
    def schema(self):
        """Dataset schema"""
        return self._schema

    @schema.setter
    def schema(self, schema):
        self._schema = schema

    def get_query(self):
        return compute_query(self)

    @property
    def dataset_info(self):
        if self._dataset_info is None:
            self._dataset_info = self._get_dataset_info()

        return self._dataset_info

    def update_dataset_info(self, privacy=None, table_name=None):
        self._dataset_info = self.dataset_info
        self._dataset_info.update(privacy=privacy, table_name=table_name)

        # update table_name if metadata table_name has been changed
        if table_name and self.table_name != self._dataset_info.table_name:
            self.table_name = self._dataset_info.table_name

    def exists(self):
        """Checks to see if table exists"""
        try:
            self._context.execute_query(
                'EXPLAIN SELECT * FROM "{table_name}"'.format(table_name=self._table_name),
                do_post=False)
            return True
        except CartoRateLimitException as err:
            raise err
        except CartoException as err:
            # If table doesn't exist, we get an error from the SQL API
            utils.debug_print(self._verbose, err=err)
            return False

    def is_public(self):
        """Checks to see if table or table used by query has public privacy"""
        public_context = get_context_with_public_creds(self._credentials)
        try:
            public_context.execute_query('EXPLAIN {}'.format(self.get_query()), do_post=False)
            return True
        except CartoRateLimitException as err:
            raise err
        except CartoException:
            return False

    def get_table_names(self):
        return [self._table_name]

    def _create_context(self):
        if self._credentials:
            return context.create_context(self._credentials)

    def _cartodbfy_query(self):
        return "SELECT CDB_CartodbfyTable('{schema}', '{table_name}')" \
            .format(schema=self._schema or self._get_schema(), table_name=self._table_name)

    def _drop_table_query(self, if_exists=True):
        return '''DROP TABLE {if_exists} {table_name}'''.format(
            table_name=self._table_name,
            if_exists='IF EXISTS' if if_exists else '')

    def _already_exists_error(self):
        return CartoException('Table with name {t} and schema {s} already exists in CARTO.'
                              'Please choose a different `table_name` or use '
                              'if_exists="replace" to overwrite it'.format(
                                  t=self._table_name, s=self._schema))

    def _is_ready_for_upload_validation(self):
        if self._table_name is None or self._credentials is None:
            raise ValueError('You should provide a table_name and credentials to upload data.')

    def _is_ready_for_dowload_validation(self):
        if self._credentials is None or (self._table_name is None and self._query is None):
            raise ValueError('You should provide a credentials and a table_name or query to download data.')

    def _copyto(self, columns, query, limit, decode_geom, retry_times):
        copy_query = """COPY ({}) TO stdout WITH (FORMAT csv, HEADER true)""".format(query)
        raw_result = self._context.download(copy_query, retry_times)

        df_types = dtypes(columns, exclude_dates=True, exclude_the_geom=True, exclude_bools=True)
        date_column_names = date_columns_names(columns)
        bool_column_names = bool_columns_names(columns)

        converters = {'the_geom': lambda x: decode_geometry(x, ENC_WKB_BHEX) if decode_geom else x}
        for bool_column_name in bool_column_names:
            converters[bool_column_name] = lambda x: convert_bool(x)

        df = pd.read_csv(raw_result, dtype=df_types,
                         parse_dates=date_column_names,
                         true_values=['t'],
                         false_values=['f'],
                         index_col='cartodb_id' if 'cartodb_id' in df_types else False,
                         converters=converters)

        if decode_geom:
            df.rename({'the_geom': 'geometry'}, axis='columns', inplace=True)

        return df

    def _get_query_columns(self):
        query = 'SELECT * FROM ({}) _q LIMIT 0'.format(self.get_query())
        table_info = self._context.execute_query(query)
        return Column.from_sql_api_fields(table_info['fields'])

    def _get_geom_type(self, query=None):
        return utils.get_query_geom_type(self._context, query or self.get_query())

    def _get_schema(self):
        if self._credentials:
            self._schema = self._context.get_schema()
            return self._schema
        else:
            return None

    def _get_dataset_info(self, table_name=None):
        return DatasetInfo(self._context, table_name or self._table_name)
