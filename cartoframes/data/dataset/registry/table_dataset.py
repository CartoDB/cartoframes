from __future__ import absolute_import

from warnings import warn

from carto.exceptions import CartoException, CartoRateLimitException

from ....utils.columns import Column, normalize_name
from ....utils.utils import is_table_name, check_credentials
from .base_dataset import BaseDataset


class TableDataset(BaseDataset):
    def __init__(self, data, credentials, schema=None):
        super(TableDataset, self).__init__(credentials)

        self._table_name = normalize_name(data)
        self._schema = schema or self._get_schema()

        if self._table_name != data:
            warn('Table will be named `{}`'.format(self._table_name))

    @staticmethod
    def can_work_with(data, credentials):
        check_credentials(credentials)
        return is_table_name(data)

    @classmethod
    def create(cls, data, credentials, schema=None):
        return cls(data, credentials, schema)

    def download(self, limit, decode_geom, retry_times):
        self._is_ready_for_dowload_validation()
        columns = self._get_table_columns()
        query = self._get_read_query(columns, limit)
        self._df = self._copyto(columns, query, limit, decode_geom, retry_times)
        return self._df

    def upload(self, if_exists, with_lnglat):
        raise ValueError('Nothing to upload. Dataset needs a DataFrame, a '
                         'GeoDataFrame or a query to upload data to CARTO.')

    def delete(self):
        if self.exists():
            self._context.execute_query(self._drop_table_query(False))
            self._unsync()
            return True

        return False

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        return self._get_geom_type()

    def get_column_names(self, exclude=None):
        """Get column names from a table"""
        columns = [c.name for c in self._get_table_columns()]

        if exclude and isinstance(exclude, list):
            columns = list(set(columns) - set(exclude))

        return columns

    def get_num_rows(self):
        """Get the number of rows in the table"""
        result = self._context.execute_query("SELECT COUNT(*) FROM {table}".format(table=self.table_name))
        return result.get('rows')[0].get('count')

    def _unsync(self):
        self._dataset_info = None

    def _get_table_columns(self):
        query = '''
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}' AND table_schema = '{schema}'
        '''.format(table=self._table_name, schema=self._schema)

        try:
            table_info = self._context.execute_query(query)
            return [Column(c['column_name'], pgtype=c['data_type']) for c in table_info['rows']]
        except CartoRateLimitException as err:
            raise err
        except CartoException as e:
            # this may happen when using the default_public API key
            if str(e) == 'Access denied':
                return self._get_query_columns()
            else:
                raise e

    def _get_read_query(self, table_columns, limit=None):
        """Create the read (COPY TO) query"""
        query_columns = [column.name for column in table_columns if column.name != 'the_geom_webmercator']

        query = 'SELECT {columns} FROM "{schema}"."{table_name}"'.format(
            table_name=self._table_name,
            schema=self._schema,
            columns=', '.join(query_columns))

        if limit is not None:
            if isinstance(limit, int) and (limit >= 0):
                query += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")

        return query
