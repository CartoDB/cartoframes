from carto.exceptions import CartoException, CartoRateLimitException

from .dataset_base import DatasetBase
from .utils import map_geom_type


class QueryDataset(DatasetBase):
    def __init__(self, data, context=None, schema=None):
        super(QueryDataset, self).__init__(context)

        self._query = data

    @property
    def query(self):
        return self._query

    @property
    def dataset_info(self):
        raise CartoException('We can not extract Dataset info from a query. Use `Dataset.from_table()` method '
                             'to get or modify the info from a CARTO table.')

    def update_dataset_info(self, privacy=None, name=None):
        raise CartoException('We can not extract Dataset info from a query. Use `Dataset.from_table()` method '
                             'to get or modify the info from a CARTO table.')

    def download(self, limit, decode_geom, retry_times):
        self._is_ready_for_dowload_validation()
        columns = self.get_query_columns()
        return self._copyto(columns, self._query, limit, decode_geom, retry_times)

    def upload(self, if_exists, with_lnglat):
        self._is_ready_for_upload_validation()

        if if_exists == DatasetBase.APPEND:
            raise CartoException('Error using append with a QueryDataset.'
                                 'It is not possible to append data to a query')
        elif if_exists == DatasetBase.REPLACE or not self.exists():
            self._create_table_from_query()
        elif if_exists == DatasetBase.FAIL:
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
            self._client.execute_long_running_query(query)
        except CartoRateLimitException as err:
            raise err
        except CartoException as err:
            raise CartoException('Cannot create table: {}.'.format(err))

    def _get_query_to_create_table_from_query(self):
        return '''CREATE TABLE {table_name} AS ({query})'''.format(table_name=self._table_name, query=self._query)

