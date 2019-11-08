from __future__ import absolute_import

from carto.exceptions import CartoException

from ...auth import get_default_credentials
from .dataset_info import DatasetInfo
from .registry.dataframe_dataset import DataFrameDataset
from .registry.strategies_registry import StrategiesRegistry
from .registry.base_dataset import BaseDataset


class Dataset(object):
    """Generic data class for cartoframes data operations. A `Dataset` instance
    can be created from a dataframe, geodataframe, a table hosted on a CARTO
    account, an arbitrary query against a CARTO account, or a local or hosted
    GeoJSON source. If hosted, the data can be retrieved as a pandas DataFrame.
    If local or as a query, a new table can be created in a CARTO account off
    of the Dataset instance.

    Examples:
        Dataframe:

        .. code::

            import pandas
            from cartoframes.data import Dataset

            df = pandas.read_csv('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv')
            ds = Dataset(df)

        GeoDataframe:

        .. code::

            import geopandas as gpd
            from cartoframes.data import Dataset

            gdf = gpd.read_file('https://opendata.arcgis.com/datasets/9485c26e98c6450e9611a2360ece965d_0.geojson')
            ds = Dataset(gdf)

        GeoJSON file:

        .. code::

            from cartoframes.data import Dataset

            ds = Dataset('path/to/geojson/file.geojson')

        Table from CARTO:

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.data import Dataset

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            ds = Dataset('table_name')

        Query against tables in user CARTO account:

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.data import Dataset

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            ds = Dataset('SELECT * FROM table_name JOIN table2 ON ...')
    """

    DOWNLOAD_RETRY_TIMES = 3

    def __init__(self, data, credentials=None, schema=None):
        self._registry = self._get_strategies_registry()
        self._strategy = self._init_strategy(data, credentials, schema)

    @property
    def credentials(self):
        """Dataset's :py:class:`Credentials <cartoframes.auth.Credentials>`

        Returns:
            :py:class:`Credentials <cartoframes.auth.Credentials>`: Credentials,
            if any, for data associated with Dataset instance.

        """
        return self._strategy.credentials

    @credentials.setter
    def credentials(self, credentials):
        """Set a new :py:class:`Credentials <cartoframes.auth.Credentials>`
        for a Dataset instance.

        Args:
            credentials (:py:class:`cartoframes.auth.Credentials`): Credentials
              instance to associated with Datset instance
        """
        self._strategy.credentials = credentials

    @property
    def table_name(self):
        """Dataset table name. If `None`, then the data is a query or DataFrame"""
        return self._strategy.table_name

    @property
    def schema(self):
        """Dataset schema"""
        return self._strategy.schema

    @property
    def query(self):
        """Dataset query"""
        return self._strategy.query

    @property
    def dataframe(self):
        """Dataset dataframe"""
        return self._strategy.dataframe

    @property
    def dataset_info(self):
        """:py:class:`DatasetInfo <cartoframes.data.DatasetInfo>` associated with Dataset instance


        .. note::
            This method only works for Datasets created from tables.

        Example:

            .. code::

               from cartoframes.auth import set_default_credentials
               from cartoframes.data import Dataset

               set_default_credentials(
                   base_url='https://your_user_name.carto.com/',
                   api_key='your api key'
               )

               d = Dataset('tablename')
               d.dataset_info

        """
        if self.is_local():
            raise CartoException('Your data is not synchronized with CARTO. If you want to upload it to CARTO, '
                                 'you should use: `Dataset.upload(table_name="new_table")` '
                                 'Then, if you want to work with the remote data, use `Dataset("new_table")`')

        return self._strategy.dataset_info

    def get_query(self):
        """Get the computed query"""
        return self._strategy.get_query()

    def get_geodataframe(self):
        """Converts DataFrame into GeoDataFrame if possible"""
        return self._strategy.get_geodataframe()

    def get_column_names(self, exclude=None):
        """Get column names from a dataset"""
        return self._strategy.get_column_names(exclude)

    def get_table_names(self):
        """Get table names used by Dataset instance"""
        if self.is_local():
            raise CartoException('Your data is not synchronized with CARTO. If you want to upload it to CARTO, '
                                 'you should use: `Dataset.upload(table_name="new_table")` '
                                 'Then, if you want to work with the remote data, use `Dataset("new_table")`')

        return self._strategy.get_table_names()

    def get_num_rows(self):
        """Get the number of rows in the dataset"""
        return self._strategy.get_num_rows()

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

    def download(self, limit=None, decode_geom=False, retry_times=DOWNLOAD_RETRY_TIMES):
        """Download / read a Dataset (table or query) from CARTO account
        associated with the Dataset's instance of :py:class:`Credentials
        <cartoframes.auth.Credentials>`.

        Args:
            limit (int, optional):
                The number of rows of the Dataset to download.
                Default is to download all rows. This value must be >= 0.
            decode_geom (bool, optional):
                Decode Dataset geometries into Shapely geometries from EWKB encoding.
            retry_times (int, optional):
                Number of time to retry the download in case it fails.
                Default is 3.

        Example:

            .. code::

                from cartoframes.data import Dataset
                from cartoframes.auth import set_default_credentials

                # use cartoframes example account
                set_default_credentials('https://cartoframes.carto.com')

                d = Dataset('brooklyn_poverty')
                df = d.download(decode_geom=True)
        """

        return self._strategy.download(limit, decode_geom, retry_times)

    IF_EXISTS_FAIL = BaseDataset.IF_EXISTS_FAIL
    """'fail' option to avoid overwritting a table.

    Example:

        .. code::

            from cartoframes.data import Dataset, DatasetInfo
            from cartoframes.auth import set_default_credentials

            set_default_credentials(
                base_url='https://your_user_name.carto.com/',
                api_key='your api key'
            )

            d = Dataset('tablename')
            d.upload(if_exists=Dataset.IF_EXISTS_FAIL, table_name='new_table')
    """

    IF_EXISTS_REPLACE = BaseDataset.IF_EXISTS_REPLACE
    """'replace' option to replace the table with the new one.

    Example:

        .. code::

            from cartoframes.data import Dataset, DatasetInfo
            from cartoframes.auth import set_default_credentials

            set_default_credentials(
                base_url='https://your_user_name.carto.com/',
                api_key='your api key'
            )

            d = Dataset('tablename')
            d.upload(if_exists=Dataset.IF_EXISTS_FAIL, table_name='new_table')
    """

    IF_EXISTS_APPEND = BaseDataset.IF_EXISTS_APPEND
    """'append' option to append the new table in the existing table.

    Example:

        .. code::

            from cartoframes.data import Dataset, DatasetInfo
            from cartoframes.auth import set_default_credentials

            set_default_credentials(
                base_url='https://your_user_name.carto.com/',
                api_key='your api key'
            )

            d = Dataset('tablename')
            d.upload(if_exists=Dataset.IF_EXISTS_APPEND, table_name='new_table')
    """

    def upload(self, with_lnglat=None, if_exists=IF_EXISTS_FAIL, table_name=None, schema=None, credentials=None):
        r"""Upload Dataset to CARTO account associated with `credentials`.

        Args:
            with_lnglat (tuple, optional): Two columns that have the longitude
              and latitude information. If used, a point geometry will be
              created upon upload to CARTO. Example input: `('long', 'lat')`.
              Defaults to `None`.
            if_exists (str, optional): Behavior for adding data from Dataset.
              Options are :py:attr:`Dataset.IF_EXISTS_FAIL`,
              :py:attr:`Dataset.IF_EXISTS_REPLACE`, or :py:attr:`Dataset.IF_EXISTS_APPEND`.
              Defaults to 'fail', which means that the Dataset instance
              will not overwrite a table of the same name if it exists.
              If the table does not exist, it will be created.
            table_name (str): Desired table name for the dataset on CARTO. If
              name does not conform to SQL naming conventions, it will be
              'normalized' (e.g., all lower case, adding `_` in place of spaces
              and other special characters.
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
              credentials of user account to send Dataset to. If not provided,
              a default credentials (if set with :py:meth:`set_default_credentials
              <cartoframes.auth.set_default_credentials>`) will attempted to be
              used.

        Example:

            Send a pandas DataFrame to CARTO:

            .. code::

                from cartoframes.auth import set_default_credentials
                from cartoframes.data import Dataset
                import pandas as pd

                set_default_credentials(
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
        elif self._strategy.credentials is None:
            self._strategy.credentials = get_default_credentials()
        if schema:
            self._strategy.schema = schema

        self._strategy.upload(if_exists, with_lnglat)

        return Dataset(self._strategy.table_name, self._strategy.credentials, self._strategy.schema)

    def delete(self):
        """Delete table on CARTO account associated with a Dataset instance

        Example:

            .. code::

                from cartoframes.data import Dataset
                from cartoframes.auth import set_default_credentials

                set_default_credentials(
                    base_url='https://your_user_name.carto.com',
                    api_key='your api key'
                )

                d = Dataset('table_name')
                d.delete()

        Returns:
            bool: True if deletion is successful, False otherwise.

        """

        return self._strategy.delete()

    PRIVACY_PRIVATE = DatasetInfo.PRIVACY_PRIVATE
    """Dataset privacy for datasets that are private.

    Example:

        .. code::

            from cartoframes.data import Dataset, DatasetInfo
            from cartoframes.auth import set_default_credentials

            set_default_credentials(
                base_url='https://your_user_name.carto.com/',
                api_key='your api key'
            )

            d = Dataset('tablename')
            d.update_dataset_info(privacy=Dataset.PRIVACY_PRIVATE)
    """

    PRIVACY_PUBLIC = DatasetInfo.PRIVACY_PUBLIC
    """Dataset privacy for datasets that are public.

    Example:

        .. code::

            from cartoframes.data import Dataset, DatasetInfo
            from cartoframes.auth import set_default_credentials

            set_default_credentials(
                base_url='https://your_user_name.carto.com/',
                api_key='your api key'
            )

            d = Dataset('tablename')
            d.update_dataset_info(privacy=Dataset.PRIVACY_PUBLIC)
    """

    PRIVACY_LINK = DatasetInfo.PRIVACY_LINK
    """Dataset privacy for datasets that are accessible by link.

    Example:

    .. code::

        from cartoframes.data import Dataset, DatasetInfo
        from cartoframes.auth import set_default_credentials

        set_default_credentials(
            base_url='https://your_user_name.carto.com/',
            api_key='your api key'
        )

        d = Dataset('tablename')
        d.update_dataset_info(privacy=Dataset.PRIVACY_LINK)
    """

    def update_dataset_info(self, privacy=None, table_name=None):
        """Update/change Dataset privacy and name

        Args:
          privacy (str, optional): One of :py:attr:`Dataset.PRIVACY_PRIVATE`,
            :py:attr:`Dataset.PRIVACY_PUBLIC` or :py:attr:`Dataset.PRIVACY_LINK`
          table_name (str, optional): Name of the dataset on CARTO. After updating it,
            the table_name will be changed too.

        Example:

            .. code::

                from cartoframes.data import Dataset, DatasetInfo
                from cartoframes.auth import set_default_credentials

                set_default_credentials(
                    base_url='https://your_user_name.carto.com/',
                    api_key='your api key'
                )

                d = Dataset('tablename')
                d.update_dataset_info(privacy=Dataset.PRIVACY_LINK)

        """

        return self._strategy.update_dataset_info(privacy, table_name)

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        return self._strategy.compute_geom_type()

    def _init_strategy(self, data, credentials=None, schema=None):
        credentials = credentials or get_default_credentials()
        for strategy in self._registry.get_strategies():
            if strategy.can_work_with(data, credentials):
                return strategy.create(data, credentials, schema)

        raise ValueError('We can not detect the Dataset type')

    def _get_strategies_registry(self):
        return StrategiesRegistry()
