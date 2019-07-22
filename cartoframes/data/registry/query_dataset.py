from carto.exceptions import CartoException, CartoRateLimitException

from ..dataset_info import DatasetInfo
from .base_dataset import BaseDataset
from ..utils import is_sql_query


class QueryDataset(BaseDataset):
    def __init__(self, data, credentials, schema=None):
        super(QueryDataset, self).__init__(credentials)

        self._query = data
        self._dataset_info = None

    @staticmethod
    def can_work_with(data):
        return is_sql_query(data)

    @classmethod
    def create(cls, data, credentials, schema=None):
        return cls(data, credentials)

    @property
    def query(self):
        return self._query

    @property
    def dataset_info(self):
        raise ValueError('The dataset_info method is not allowed on Datasets built on queries. '
                         'Use a table-based dataset instead: Dataset(my_table)')

    def update_dataset_info(self, privacy=None, table_name=None):
        raise ValueError('The dataset_info method is not allowed on Datasets built on queries. '
                         'Use a table-based dataset instead: Dataset(my_table)')

    def download(self, limit, decode_geom, retry_times):
        self._is_ready_for_dowload_validation()
        columns = self._get_query_columns()
        return self._copyto(columns, self._query, limit, decode_geom, retry_times)

    def upload(self, if_exists, with_lnglat):
        self._is_ready_for_upload_validation()

        if if_exists == BaseDataset.APPEND:
            raise CartoException('Error using append with a QueryDataset.'
                                 'It is not possible to append data to a query')
        elif if_exists == BaseDataset.REPLACE or not self.exists():
            self._create_table_from_query()
        elif if_exists == BaseDataset.FAIL:
            raise self._already_exists_error()

    def delete(self):
        raise ValueError('The delete method is not allowed on Datasets built on queries. '
                         'Use a table-based dataset instead: Dataset(my_table)')

    def get_query(self):
        return self._query

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        return self._get_geom_type(self._query)

    def _create_table_from_query(self):
        query = '''BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'''.format(
            drop=self._drop_table_query(),
            create=self._get_query_to_create_table_from_query(),
            cartodbfy=self._cartodbfy_query())

        try:
            self._context.execute_long_running_query(query)
        except CartoRateLimitException as err:
            raise err
        except CartoException as err:
            raise CartoException('Cannot create table: {}.'.format(err))

    def _get_query_to_create_table_from_query(self):
        return '''CREATE TABLE {table_name} AS ({query})'''.format(table_name=self._table_name, query=self._query)

    def _get_tables_used_by_query(self):
        query = "SELECT CDB_QueryTablesText('{}') as tables".format(self._query)
        result = self._context.execute_query(query)
        tables = []
        if result['total_rows'] > 0:
            # Dataset_info only works with tables without schema
            for t in result['rows'][0]['tables']:
                if '.' in t:
                    _, table_name = t.split('.')
                    tables.append(table_name)
                else:
                    tables.append(t)

        return tables
