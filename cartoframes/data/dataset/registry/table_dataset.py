from __future__ import absolute_import

from carto.exceptions import CartoException, CartoRateLimitException

from ....utils.columns import Column
from .base_dataset import BaseDataset


class TableDataset(BaseDataset):
    def __init__(self, data, credentials, schema=None):
        pass

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
