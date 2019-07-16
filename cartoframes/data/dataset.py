import pandas as pd

from .dataframe_dataset import DataFrameDataset
from .query_dataset import QueryDataset
from .table_dataset import TableDataset
from .dataset_info import DatasetInfo
from ..geojson import load_geojson
from .utils import GEOM_TYPE_POINT, GEOM_TYPE_LINE, GEOM_TYPE_POLYGON, is_sql_query, is_geojson_file_path, \
    is_table_name, _save_index_as_column

DOWNLOAD_RETRY_TIMES = 3


class Dataset(object):
    FAIL = TableDataset.FAIL
    REPLACE = TableDataset.REPLACE
    APPEND = TableDataset.APPEND

    PRIVATE = DatasetInfo.PRIVATE
    PUBLIC = DatasetInfo.PUBLIC
    LINK = DatasetInfo.LINK

    GEOM_TYPE_POINT = GEOM_TYPE_POINT
    GEOM_TYPE_LINE = GEOM_TYPE_LINE
    GEOM_TYPE_POLYGON = GEOM_TYPE_POLYGON

    def __init__(self, data, credentials=None, schema=None):
        self._strategy = self._init_strategy(data, credentials, schema)
        self._is_saved_in_carto = self._init_saved_in_carto()

    def _init_strategy(self, data, credentials=None, schema=None):
        credentials = credentials or _get_default_credentials()

        if isinstance(data, pd.DataFrame):
            return self._getDataFrameDataset(data)
        elif isinstance(data, (list, dict)):
            return self._getDataFrameDataset(load_geojson(data))
        elif isinstance(data, str):
            if is_sql_query(data):
                return self._getQueryDataset(data, credentials)
            elif is_geojson_file_path(data):
                return self._getDataFrameDataset(load_geojson(data))
            elif is_table_name(data):
                return self._getTableDataset(data, credentials, schema)

        raise ValueError('We can not detect the Dataset type')

    def _init_saved_in_carto(self):
        return self.is_remote()

    def _set_strategy(self, strategy, data, credentials=None, schema=None):
        self._strategy = strategy(data, credentials, schema)

    def _getDataFrameDataset(self, data):
        _save_index_as_column(data)
        return DataFrameDataset(data)

    def _getQueryDataset(self, data, credentials):
        return QueryDataset(data, credentials)

    def _getTableDataset(self, data, credentials, schema):
        return TableDataset(data, credentials, schema)

    @property
    def credentials(self):
        """Dataset :py:class:`Context <cartoframes.auth.Context>`"""
        return self._strategy.credentials

    @credentials.setter
    def credentials(self, credentials):
        """Set a new :py:class:`Context <cartoframes.auth.Context>` for a Dataset instance."""
        self._strategy.credentials = credentials

    @property
    def table_name(self):
        """Dataset table name"""
        return self._strategy.table_name

    @property
    def schema(self):
        """Dataset schema"""
        return self._strategy.schema

    @property
    def query(self):
        """Dataset query"""
        return self._strategy.query

    def get_query(self):
        return self._strategy.get_query()

    @property
    def dataframe(self):
        """Dataset DataFrame"""
        return self._strategy.dataframe

    def get_geodataframe(self):
        """Converts DataFrame into GeoDataFrame if possible"""
        return self._strategy.get_geodataframe()

    @property
    def is_saved_in_carto(self):
        """Property on whether Dataset is saved in CARTO account"""
        return self._is_saved_in_carto

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
        if not self._is_saved_in_carto:
            raise CartoException('Your data is not synchronized with CARTO.'
                                 'First of all, you should call upload method '
                                 'to save your data in CARTO.')

        return self._strategy.dataset_info

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
        return self._strategy.update_dataset_info(privacy, name)

    def download(self, limit=None, decode_geom=False, retry_times=DOWNLOAD_RETRY_TIMES):
        """Download / read a Dataset (table or query) from CARTO account
        associated with the Dataset's instance of :py:class:`Context
        <cartoframes.auth.Context>`.
        Args:
            limit (int, optional): The number of rows of the Dataset to
              download. Default is to download all rows. This value must be
              >= 0.
            decode_geom (bool, optional): Decode Dataset geometries into
              Shapely geometries from EWKB encoding.
            retry_times (int, optional): Number of time to retry the download
              in case it fails. Default is Dataset.DOWNLOAD_RETRY_TIMES.
        Example:
            .. code::
                from cartoframes.data import Dataset
                from cartoframes.auth import set_default_context
                # use cartoframes example account
                set_default_context('https://cartoframes.carto.com')
                d = Dataset('brooklyn_poverty')
                df = d.download(decode_geom=True)
        """
        data = self._strategy.download(limit, decode_geom, retry_times)

        table_name = self._strategy.table_name
        credentials = self._strategy.credentials
        schema = self._strategy.schema

        self._set_strategy(DataFrameDataset, data)

        self._strategy.table_name = table_name
        self._strategy.credentials = credentials
        self._strategy.schema = schema

        return data

    def upload(self, with_lnglat=None, if_exists=FAIL, table_name=None, schema=None, credentials=None):
        """Upload Dataset to CARTO account associated with `credentials`.
        Args:
            with_lnglat (tuple, optional): Two columns that have the longitude
              and latitude information. If used, a point geometry will be
              created upon upload to CARTO. Example input: `('long', 'lat')`.
              Defaults to `None`.
            if_exists (str, optional): Behavior for adding data from Dataset.
              Options are 'fail', 'replace', or 'append'. Defaults to 'fail',
              which means that the Dataset instance will not overwrite a
              table of the same name if it exists. If the table does not exist,
              it will be created.
            table_name (str): Desired table name for the dataset on CARTO. If
              name does not conform to SQL naming conventions, it will be
              'normalized' (e.g., all lower case, adding `_` in place of spaces
              and other special characters.
            credentials (:py:class:`Context <cartoframes.auth.Context>`, optional):
              credentials of user account to send Dataset to. If not provided,
              a default credentials (if set with :py:meth:`set_default_context
              <cartoframes.auth.set_default_context>`) will attempted to be
              used.
        Example:
            Send a pandas DataFrame to CARTO.
            .. code::
                from cartoframes.auth import set_default_context
                from cartoframes.data import Dataset
                import pandas as pd
                set_default_context(
                    base_url='https://your_user_name.carto.com',
                    api_key='your api key'
                )
                df = pd.DataFrame({
                    'lat': [40, 45, 50],
                    'lng': [-80, -85, -90]
                })
                d = Dataset(df)
                d.upload(with_lnglat=('lng', 'lat'), table_name='sample_table')
        """
        if table_name:
            self._strategy.table_name = table_name
        if credentials:
            self._strategy.credentials = credentials
        if schema:
            self._strategy.schema = schema

        self._strategy.upload(if_exists, with_lnglat)
        self._is_saved_in_carto = True

        if isinstance(self._strategy, QueryDataset):
            self._set_strategy(
                TableDataset,
                self._strategy.table_name,
                self._strategy.credentials,
                self._strategy.schema)

        return self

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
        return self._strategy.delete()

    def exists(self):
        """Checks to see if table exists"""
        return self._strategy.exists()

    def is_public(self):
        """Checks to see if table or table used by query has public privacy"""
        return self._strategy.is_public()

    def is_local(self):
        """Checks if the Dataset is local (DataFrameDataset)"""
        return isinstance(self._strategy, DataFrameDataset)

    def is_remote(self):
        """Checks if the Dataset is local (TableDataset or QueryDataset)"""
        return not self.is_local()

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        return self._strategy.compute_geom_type()

    def get_table_column_names(self, exclude=None):
        """Get column names and types from a table"""
        return self._strategy.get_table_column_names(exclude)


def _get_default_credentials():
    from ..auth import _default_context
    return _default_context
