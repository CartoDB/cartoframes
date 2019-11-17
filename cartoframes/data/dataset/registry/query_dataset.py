from __future__ import absolute_import

from .base_dataset import BaseDataset


class QueryDataset(BaseDataset):
    def __init__(self, data, credentials, schema=None):
        pass

    def get_table_names(self):
        query = "SELECT CDB_QueryTablesText('{}') as tables".format(self._query)
        result = self._context.execute_query(query)
        tables = []
        if result['total_rows'] > 0 and result['rows'][0]['tables']:
            # Dataset_info only works with tables without schema
            tables = [table.split('.')[1] if '.' in table else table for table in result['rows'][0]['tables']]

        return tables

    def get_column_names(self, exclude=None):
        """Get column names"""
        columns = [c.name for c in self._get_query_columns()]

        if exclude and isinstance(exclude, list):
            columns = list(set(columns) - set(exclude))

        return columns

    def get_num_rows(self):
        """Get the number of rows in the query"""
        result = self._context.execute_query("SELECT COUNT(*) FROM ({query}) _query".format(query=self.get_query()))
        return result.get('rows')[0].get('count')
