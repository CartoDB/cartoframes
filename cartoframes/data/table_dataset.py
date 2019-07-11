from .dataset_base import DatasetBase
from ..columns import normalize_name
from .utils import map_geom_type

class TableDataset(DatasetBase):
    def __init__(self, data, context=None, schema=None):
        super(TableDataset, self).__init__(context,)

        self._table_name = normalize_name(data)
        self._schema = schema or self._get_schema()
        self._dataset_info = None
        self._normalized_column_names = None

        if self._table_name != data:
            warn('Table will be named `{}`'.format(table_name))

    @property
    def dataset_info(self):
        """:py:class:`DatasetInfo <cartoframes.data.DatasetInfo>` associated with Dataset instance


        .. note::
            This method only works for Datasets created from tables.

        Example:

            .. code::

               from cartoframes.auth import set_default_context
               from cartoframes.data import Dataset

               set_default_context(
                   base_url='https://your_user_name.carto.com/',
                   api_key='your api key'
               )

               d = Dataset('tablename')
               d.dataset_info

        """
        if self._dataset_info is None:
            self._dataset_info = self._get_dataset_info()

        return self._dataset_info

    def update_dataset_info(self, privacy=None, name=None):
        """Update/change Dataset privacy and name

        Args:
          privacy (str, optional): One of DatasetInfo.PRIVATE,
            DatasetInfo.PUBLIC, or DatasetInfo.LINK
          name (str, optional): Name of the dataset on CARTO.

        Example:

            .. code::

                from cartoframes.data import Dataset
                from cartoframes.auth import set_default_context

                set_default_context(
                    base_url='https://your_user_name.carto.com/',
                    api_key='your api key'
                )

                d = Dataset('tablename')
                d.update_dataset_info(privacy='link')

        """
        self._dataset_info = self.dataset_info
        self._dataset_info.update(privacy=privacy, name=name)

    def download(self, limit, decode_geom, retry_times):
        self._is_ready_for_dowload_validation()
        columns = self._get_table_columns()
        query = self._get_read_query(columns, limit)
        return self._copyto(columns, query, limit, decode_geom, retry_times)

    def upload(self):
        raise ValueError('Nothing to upload. Dataset needs a DataFrame, a '
                         'GeoDataFrame, or a query to upload data to CARTO.')

    def delete(self):
        """Delete table on CARTO account associated with a Dataset instance

        Example:

            .. code::

                from cartoframes.data import Dataset
                from cartoframes.auth import set_default_context

                set_default_context(
                    base_url='https://your_user_name.carto.com',
                    api_key='your api key'
                )

                d = Dataset('table_name')
                d.delete()

        Returns:
            bool: True if deletion is successful, False otherwise.

        """
        if self.exists():
            self._client.execute_query(self._drop_table_query(False))
            self._unsync()
            return True

        return False

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        return self._get_geom_type()

    def get_table_column_names(self, exclude=None):
        """Get column names and types from a table"""
        columns = [c.name for c in self._get_table_columns()]

        if exclude and isinstance(exclude, list):
            columns = list(set(columns) - set(exclude))

        return columns

    def _unsync(self):
        # self._is_saved_in_carto = False
        self._dataset_info = None

    def _get_table_columns(self):
        query = '''
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}' AND table_schema = '{schema}'
        '''.format(table=self._table_name, schema=self._schema)

        try:
            table_info = self._client.execute_query(query)
            return [Column(c['column_name'], pgtype=c['data_type']) for c in table_info['rows']]
        except CartoRateLimitException as err:
            raise err
        except CartoException as e:
            # this may happen when using the default_public API key
            if str(e) == 'Access denied':
                return self.get_columns()
            else:
                raise e

    def _get_dataset_info(self):
        return DatasetInfo(self._con, self._table_name)

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
