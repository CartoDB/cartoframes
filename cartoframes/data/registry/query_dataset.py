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
        if self._dataset_info is None:
            tables = self._get_tables_used_by_query()
            if not tables or len(tables) == 0:
                raise CartoException('We can not extract the table/s used by the QueryDataset, so we can not get the '
                                     'Dataset info. Try using `Dataset(table_name)` instead if possible.')
            elif len(tables) == 1:
                self._dataset_info = self._get_dataset_info(tables[0])
            else:
                self._dataset_info = {}
                for table_name in tables:
                    self._dataset_info[table_name] = self._get_dataset_info(table_name)

        return self._dataset_info

    def update_dataset_info(self, privacy=None, name=None, table_name=None):
        self._dataset_info = self.dataset_info
        if isinstance(self._dataset_info, DatasetInfo):
            self._dataset_info.update(privacy=privacy, name=name)
        elif table_name:
            self._dataset_info[table_name].update(privacy=privacy, name=name)
        else:
            for dataset_info in self._dataset_info.itervalues():
                dataset_info.update(privacy=privacy, name=name)

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
        raise ValueError('Method not allowed in QueryDataset. You should use a TableDataset: `Dataset(my_table)`')

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
