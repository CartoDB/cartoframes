from geopandas import GeoDataFrame

from .dataset.registry.base_dataset import BaseDataset
from .dataset.registry.table_dataset import TableDataset
from .dataset.registry.query_dataset import QueryDataset
from .dataset.registry.dataframe_dataset import DataFrameDataset

from ..auth.defaults import get_default_credentials
from ..utils.utils import is_sql_query, is_table_name

# TODO: This class reuses existing classes from the dataset registry.
# The implementation is temporary and will be refactored when the Dataset is removed.

DOWNLOAD_RETRY_TIMES = 3


class CartoDataFrame(GeoDataFrame):
    """Generic data class for cartoframes data operations. A `CartoDataFrame` instance
    extends from DataFrame/GeoDataFrame and allows to manage your data in the CARTO platform.
    It provides methods to upload and download your data, using table names or SQL queries,
    methods to manage your tables and also visualize your local/remote data in a map.

    Examples:
        Manage local data:

        .. code::

            from cartoframes.data import CartoDataFrame

            cdf = CartoDataFrame(df)
            cdf = CartoDataFrame.from_file('path_to_file.geojson')
            cdf = CartoDataFrame.from_features([...])

        Manage data from CARTO:

        .. code::

            from cartoframes.data import CartoDataFrame
            from cartoframes.auth import set_default_credentials

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            cdf = CartoDataFrame.from_table('table_name')
                  # or CartoDataFrame('table_name')

            cdf = CartoDataFrame.from_query('SELECT * FROM table_name')
                  # or CartoDataFrame('SELECT * FROM table_name')

    """

    def __init__(self, *args, **kwargs):
        schema = kwargs.pop('schema', None)
        download = kwargs.pop('download', True)
        credentials = kwargs.pop('credentials', None) or get_default_credentials()
        data, args, kwargs = _extract_data_arg(args, kwargs)

        super(CartoDataFrame, self).__init__(*args, **kwargs)

        self._strategy = self._create_strategy(data, schema, credentials)

        if download and not isinstance(self._strategy, DataFrameDataset):
            self.download()

    @classmethod
    def from_table(cls, table_name, schema=None, credentials=None, download=True):
        """Create a CartoDataFrame from a table.

        Args:
            table_name (str): The name of the table.
            schema (str, optional): The name of the schema.
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                The credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.

        Returns:
            :py:class:`CartoDataFrame <cartoframes.data.CartoDataFrame>`

        """
        return cls(table_name, schema=schema, credentials=credentials, download=download)

    @classmethod
    def from_query(cls, query, credentials=None, download=True):
        """Create a CartoDataFrame from a SQL query.

        Args:
            query (str): The SQL query string.
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                The credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.

        Returns:
            :py:class:`CartoDataFrame <cartoframes.data.CartoDataFrame>`

        """
        return cls(query, credentials=credentials, download=download)

    @classmethod
    def from_file(cls, filename, **kwargs):
        """Create a CartoDataFrame from a file.

        Returns:
            :py:class:`CartoDataFrame <cartoframes.data.CartoDataFrame>`

        """
        gdf = GeoDataFrame.from_file(filename, **kwargs)
        return cls(gdf)

    @classmethod
    def from_features(cls, features, crs=None, columns=None):
        """Create a CartoDataFrame from a list of features.

        Returns:
            :py:class:`CartoDataFrame <cartoframes.data.CartoDataFrame>`

        """
        gdf = GeoDataFrame.from_features(features, crs, columns)
        return cls(gdf)

    def download(self, limit=None, decode_geom=None, retry_times=DOWNLOAD_RETRY_TIMES,
                 table_name=None, schema=None, credentials=None):
        """Download / read data from a CARTO account associated with `credentials`.

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

                from cartoframes.data import CartoDataFrame
                from cartoframes.auth import set_default_credentials

                # use cartoframes example account
                set_default_credentials('https://cartoframes.carto.com')

                cdf = CartoDataFrame('brooklyn_poverty')
                cdf.download(limit=5, decode_geom=True)

        Returns:
            :py:class:`CartoDataFrame <cartoframes.data.CartoDataFrame>`

        """
        self._update_strategy(table_name, schema, credentials)
        df = self._strategy.download(limit, decode_geom, retry_times)
        if df is not None:
            object.__setattr__(self, '_data', df._data)
        return self

    def upload(self, table_name=None, schema=None, with_lnglat=False,
               if_exists=BaseDataset.IF_EXISTS_FAIL, credentials=None):
        """Upload / write data to a CARTO account associated with `credentials`.

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
            table_name (str, optional): Desired table name for the dataset on CARTO. If
              name does not conform to SQL naming conventions, it will be
              'normalized' (e.g., all lower case, adding `_` in place of spaces
              and other special characters.
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
              credentials of user account to send Dataset to. If not provided,
              a default credentials (if set with :py:meth:`set_default_credentials
              <cartoframes.auth.set_default_credentials>`) will attempted to be
              used.

        Example:

            Write local data into CARTO:

            .. code::

                from cartoframes.auth import set_default_credentials
                from cartoframes.data import CartoDataFrame

                set_default_credentials(
                    base_url='https://your_user_name.carto.com',
                    api_key='your api key'
                )

                cdf = CartoDataFrame({
                    'lat': [40, 45, 50],
                    'lng': [-80, -85, -90]
                })
                cdf.upload(with_lnglat=('lng', 'lat'), table_name='sample_table')
        """
        self._update_strategy(table_name, schema, credentials)
        self._strategy.upload(if_exists, with_lnglat)
        print('Data uploaded successfully!')

    def delete(self):
        """Delete a table on a CARTO account associated with `credentials`.

        Example:

            .. code::

                from cartoframes.data import CartoDataFrame
                from cartoframes.auth import set_default_credentials

                set_default_credentials(
                    base_url='https://your_user_name.carto.com',
                    api_key='your api key'
                )

                cdf = CartoDataFrame('table_name')
                cdf.delete()

        Returns:
            bool: True if deletion is successful, False otherwise.

        """
        return self._strategy.delete()

    def update_info(self, table_name=None, privacy=None):
        """Update / change a table name and privacy.

        Args:
            table_name (str, optional): Name of the dataset on CARTO. After updating it,
                the table_name will be changed too.
            privacy (str, optional): One of :py:attr:`PRIVACY_PRIVATE`,
                :py:attr:`PRIVACY_PUBLIC` or :py:attr:`PRIVACY_LINK`

        Example:

            .. code::

                from cartoframes.data import CartoDataFrame
                from cartoframes.auth import set_default_credentials

                set_default_credentials(
                    base_url='https://your_user_name.carto.com/',
                    api_key='your api key'
                )

                cdf = CartoDataFrame('tablename')
                cdf.update_info(privacy=PRIVACY_LINK)

        """
        return self._strategy.update_dataset_info(privacy, table_name)

    def exists(self):
        """Checks to see if the table exists in a CARTO account."""
        return self._strategy.exists()

    def is_public(self):
        """Checks to see if table or table used by query has public privacy."""
        return self._strategy.is_public()

    def num_rows(self):
        """Gets the number of rows of the CartoDataFrame."""
        return self._strategy.get_num_rows()

    def geom_type(self):
        """Computes the geometry type of the CartoDataFrame."""
        return self._strategy.compute_geom_type()

    def map(self, *args, ** kwargs):
        """Renders the data in a CARTO map.

         Returns:
            :py:class:`Map <cartoframes.viz.Map>`
        """
        from ..viz import Map, Layer
        return Map(Layer(self, *args, **kwargs))

    def is_local(self):
        return isinstance(self._strategy, DataFrameDataset)

    def is_remote(self):
        return not self.is_local()

    def get_query(self):
        return self._strategy.get_query()

    def _create_strategy(self, data, schema, credentials):
        if data is not None:
            if is_sql_query(data) and QueryDataset.can_work_with(data, credentials):
                return QueryDataset.create(data, credentials)
            elif is_table_name(data) and TableDataset.can_work_with(data, credentials):
                return TableDataset.create(data, credentials, schema)
        return DataFrameDataset.create(self, credentials)

    def _update_strategy(self, table_name, schema, credentials):
        if table_name is not None:
            self._strategy.table_name = table_name
        if schema is not None:
            self._strategy.schema = schema
        if credentials is not None:
            self._strategy.credentials = credentials

        if self._strategy.credentials is None:
            # Apply default credentials
            self._strategy.credentials = get_default_credentials()


def _extract_data_arg(args, kwargs):
    data = None

    if len(args):
        data = args[0]

        if isinstance(data, str):
            args = list(args)
            args[0] = None
            args = tuple(args)

    elif 'data' in kwargs:
        data = kwargs['data']

        if isinstance(data, str):
            kwargs['data'] = None

    return data, args, kwargs
