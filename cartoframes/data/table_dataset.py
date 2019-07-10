from .dataset_base import DatasetBase
from ..columns import normalize_name


class TableDataset(DatasetBase):
    def __init__(self, data, context=None, schema=None):
        super(TableDataset, self).__init__(context,)
        self._state = DatasetBase.STATE_REMOTE

        self._table_name = normalize_name(data)
        self._schema = schema or self._get_schema()
        self._dataset_info = None
        self._normalized_column_names = None
        self._client = self._get_client()

        if self.data != data:
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

               d = Dataset.from_table('tablename')
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

                d = Dataset.from_table('tablename')
                d.update_dataset_info(privacy='link')

        """
        self._dataset_info = self.dataset_info
        self._dataset_info.update(privacy=privacy, name=name)

    def download(self):
        pass

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

                d = Dataset.from_table('table_name')
                d.delete()

        Returns:
            bool: True if deletion is successful, False otherwise.

        """
        if self.exists():
            self._client.execute_query(self._drop_table_query(False))
            self._unsync()
            return True

        return False

    def _unsync(self):
        # self._is_saved_in_carto = False
        self._dataset_info = None
