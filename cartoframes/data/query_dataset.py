from .dataset_base import DatasetBase


class QueryDataset(DatasetBase):
    def __init__(self, data, context):
        super(QueryDataset, self).__init__(context)
        self._state = DatasetBase.STATE_REMOTE

        self._query = data

    def download(self):
        pass

    def upload(self, with_lnglat, if_exists):
        self._is_ready_for_upload_validation()

        if if_exists == DatasetBase.APPEND:
            raise CartoException('Error using append with a QueryDataset.'
                                 'It is not possible to append data to a query')
        elif if_exists == DatasetBase.REPLACE or not self.exists():
            self._create_table_from_query()
            # self._is_saved_in_carto = True
        elif if_exists == DatasetBase.FAIL:
            raise self._already_exists_error()

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
