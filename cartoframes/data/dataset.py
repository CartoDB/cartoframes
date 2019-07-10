"""Dataset
======="""
import pandas as pd
from tqdm import tqdm
from warnings import warn

from carto.exceptions import CartoException, CartoRateLimitException

from ..client import create_client
from .utils import decode_geometry, detect_encoding_type, compute_query, compute_geodataframe, \
    get_client_with_public_creds, convert_bool, ENC_WKB_BHEX
from .dataset_info import DatasetInfo
from ..columns import Column, normalize_names, normalize_name, dtypes, date_columns_names, bool_columns_names
from ..geojson import load_geojson

# avoid _lock issue: https://github.com/tqdm/tqdm/issues/457
tqdm(disable=True, total=0)  # initialise internal lock

DOWNLOAD_RETRY_TIMES = 3


class Dataset(object):
    """Generic data class for cartoframes data operations. A `Dataset` instance
    can be created from a dataframe, geodataframe, a table hosted on a CARTO
    account, an arbitrary query against a CARTO account, or a local or hosted
    GeoJSON source. If hosted, the data can be retrieved as a pandas DataFrame.
    If local or as a query, a new table can be created in a CARTO account off
    of the Dataset instance.

    The recommended way to work with this class is by using the class methods
    :py:meth:`from_table`, :py:meth:`from_query`, :py:meth:`from_dataframe`,
    :py:meth:`from_geodataframe`, or :py:meth:`from_geojson`. Direct use of the
    Dataset constructor should be avoided.
    """
    FAIL = 'fail'
    REPLACE = 'replace'
    APPEND = 'append'

    PRIVATE = DatasetInfo.PRIVATE
    PUBLIC = DatasetInfo.PUBLIC
    LINK = DatasetInfo.LINK

    STATE_LOCAL = 'local'
    STATE_REMOTE = 'remote'

    GEOM_TYPE_POINT = 'point'
    GEOM_TYPE_LINE = 'line'
    GEOM_TYPE_POLYGON = 'polygon'

    def __init__(self, table_name=None, schema=None, query=None, df=None,
                 state=None, is_saved_in_carto=False, context=None):
        from ..auth import _default_context
        self._con = context or _default_context

        self._table_name = normalize_name(table_name)
        self._schema = schema or self._get_schema()
        self._query = query
        self._df = df

        if not self._validate_init():
            raise ValueError('Improper dataset creation. You should use one of the class methods: '
                             'from_table, from_query, from_dataframe, from_geodataframe, from_geojson')

        self._client = self._create_client()

        self._state = state
        self._is_saved_in_carto = is_saved_in_carto
        self._dataset_info = None

        self._normalized_column_names = None

        if self._table_name != table_name:
            warn('Table will be named `{}`'.format(table_name))

    @classmethod
    def from_table(cls, table_name, context=None, schema=None):
        """Create a :py:class:`Dataset <cartoframes.data.Dataset>` from a table
        hosted on CARTO.

        Args:
          table_name (str): Name of table on CARTO account associated with
            `context`.
          context (:py:class:`Context <cartoframes.auth.Context>`, optional):
            Context that `table_name` is associated with. If
            `set_default_context` is previously used, this value will be
            implicitly filled in.
          schema (str, optional): Name of user in organization (multi-user
            account) who shared `table_name`. This option only works with
            multi-user accounts.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.data import Dataset

            set_default_context('https://cartoframes.carto.com')

            d = Dataset.from_table('us_counties_population')

            # download into a dataframe
            df = d.download()

        """
        return cls(table_name=table_name, schema=schema, context=context,
                   state=cls.STATE_REMOTE, is_saved_in_carto=True)

    @classmethod
    def from_query(cls, query, context=None):
        """Create a Dataset from an arbitrary query of data hosted on CARTO.

        Args:
          query (str): Name of table on CARTO account associated with
            `context`.
          context (:py:class:`Context <cartoframes.auth.Context>`, optional):
            Context that `query` is associated with. If
            :py:meth:`set_default_context <cartoframes.auth.set_default_context>`
            is previously used, this value will be implicitly filled in.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.data import Dataset
            from cartoframes.viz import Map
            from cartoframes.viz.helpers import color_continuous_layer

            set_default_context('https://cartoframes.carto.com')

            d = Dataset.from_query('''
                SELECT
                  CDB_LatLng(pickup_latitude, pickup_longitude) as the_geom,
                  ST_Transform(CDB_LatLng(pickup_latitude, pickup_longitude), 3857) as the_geom_webmercator,
                  cartodb_id,
                  fare_amount
                FROM
                  taxi_50k
                ''')

            # show dataset on a map
            Map(color_continuous_layer(d, 'fare_amount'))

        """
        return cls(query=query, context=context, state=cls.STATE_REMOTE, is_saved_in_carto=True)

    @classmethod
    def from_dataframe(cls, df):
        """Create a Dataset from a local pandas DataFrame.

        Args:
          df (pandas.DataFrame): pandas DataFrame

        Example:

            Create a Dataset from a pandas Dataframe and then map the data.

            .. code::

                from cartoframes.data import Dataset
                from cartoframes.viz import Map, Layer
                import pandas as pd

                df = pd.DataFrame({'lat': [0, 10, 20], 'lng': [20, 10, 0]})

                d = Dataset.from_dataframe(df)

                Map(Layer(d))

        """
        dataset = cls(df=df, state=cls.STATE_LOCAL)
        _save_index_as_column(dataset._df)
        return dataset

    @classmethod
    def from_geodataframe(cls, gdf):
        """Create a Dataset from a local GeoPandas GeoDataFrame.

        Args:
          gdf (geopandas.GeoDataFrame): GeoPandas GeoDataFrame

        Example:

          GeoDataFrame example code taken from `GeoPandas documentation
          <http://geopandas.org/gallery/create_geopandas_from_pandas.html#creating-a-geodataframe-from-a-dataframe-with-coordinates>`__.

        .. code::

            from cartoframes.data import Dataset
            from cartoframes.viz import Map, Layer
            import pandas as pd
            import geopandas as gpd

            df = pd.DataFrame(
                {'City': ['Buenos Aires', 'Brasilia', 'Santiago', 'Bogota', 'Caracas'],
                 'Country': ['Argentina', 'Brazil', 'Chile', 'Colombia', 'Venezuela'],
                 'Latitude': [-34.58, -15.78, -33.45, 4.60, 10.48],
                 'Longitude': [-58.66, -47.91, -70.66, -74.08, -66.86]})
            gdf = gpd.GeoDataFrame(
                df,
                geometry=gpd.points_from_xy(df.Longitude, df.Latitude)
            )

            d = Dataset.from_geodataframe(gdf)

            Map(Layer(d))

        """
        dataset = cls(df=gdf, state=cls.STATE_LOCAL)
        _save_index_as_column(dataset._df)
        return dataset

    @classmethod
    def from_geojson(cls, geojson):
        """Create a Dataset from a GeoJSON file (hosted or local).

        Args:
          gdf (geopandas.GeoDataFrame): GeoPandas GeoDataFrame

        Example:

          GeoDataFrame example code taken from `GeoPandas documentation
          <http://geopandas.org/gallery/create_geopandas_from_pandas.html#creating-a-geodataframe-from-a-dataframe-with-coordinates>`__.

        .. code::

            from cartoframes.data import Dataset
            from cartoframes.viz import Map, Layer

            geojson_source = 'https://cartoframes.carto.com/api/v2/sql?q=select+*+from+nyc_census_tracts&format=geojson'

            d = Dataset.from_geojson(geojson_source)

            Map(Layer(d))
        """
        return cls(df=load_geojson(geojson), state=cls.STATE_LOCAL)

    @property
    def dataframe(self):
        """Dataset DataFrame"""
        return self._df

    def get_geodataframe(self):
        """Converts DataFrame into GeoDataFrame if possible"""
        gdf = compute_geodataframe(self)
        if not gdf.empty:
            self._df = gdf

        return self._df

    @property
    def table_name(self):
        """Dataset table name"""
        return self._table_name

    @property
    def schema(self):
        """Dataset schema"""
        return self._schema

    @property
    def query(self):
        """Dataset query"""
        return self._query

    def get_query(self):
        if self.query is None:
            return compute_query(self)
        else:
            return self._query

    @property
    def context(self):
        """Dataset :py:class:`Context <cartoframes.auth.Context>`"""
        return self._con

    @context.setter
    def context(self, context):
        """Set a new :py:class:`Context <cartoframes.auth.Context>` for a Dataset instance."""
        self._con = context
        self._schema = context.get_default_schema()
        self._client = self._create_client()

    @property
    def is_saved_in_carto(self):
        """Property on whether Dataset is saved in CARTO account"""
        return self._is_saved_in_carto

    @property
    def dataset_info(self):

        if not self._is_saved_in_carto:
            raise CartoException('Your data is not synchronized with CARTO.'
                                 'First of all, you should call upload method '
                                 'to save your data in CARTO.')

        if not self._table_name and self._query:
            raise CartoException('We can not extract Dataset info from a '
                                 'query. Use `Dataset.from_table()` method '
                                 'to get or modify the info from a CARTO table.')

        if self._dataset_info is None:
            self._dataset_info = self._get_dataset_info()

        return self._dataset_info

    def update_dataset_info(self, privacy=None, name=None):

        self._dataset_info = self.dataset_info
        self._dataset_info.update(privacy=privacy, name=name)

    def upload(self, with_lnglat=None, if_exists=FAIL, table_name=None, schema=None, context=None):


        return self

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



    def is_public(self):
        """Checks to see if table or table used by query has public privacy"""
        public_client = get_client_with_public_creds(self.context)
        try:
            public_client.execute_query('EXPLAIN {}'.format(self.get_query()), do_post=False)
            return True
        except CartoRateLimitException as err:
            raise err
        except CartoException:
            return False

    def _create_client(self):
        if self._con:
            return create_client(self._con.creds, self._con.session)

    def _create_table(self, with_lnglat=None):
        query = '''BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'''.format(
            drop=self._drop_table_query(),
            create=self._create_table_query(with_lnglat),
            cartodbfy=self._cartodbfy_query())

        try:
            self._client.execute_long_running_query(query)
        except CartoRateLimitException as err:
            raise err
        except CartoException as err:
            raise CartoException('Cannot create table: {}.'.format(err))

    def _validate_init(self):
        inputs = [self._table_name, self._query, self._df]
        inputs_number = sum(x is not None for x in inputs)

        if inputs_number != 1:
            return False

        return True








    def _create_table_query(self, with_lnglat=None):
        if with_lnglat is None:
            geom_type = _get_geom_col_type(self._df)
        else:
            geom_type = 'Point'

        col = ('{col} {ctype}')
        cols = ', '.join(col.format(col=norm,
                                    ctype=_dtypes2pg(self._df.dtypes[orig]))
                         for norm, orig in self._normalized_column_names)

        if geom_type:
            cols += ', {geom_colname} geometry({geom_type}, 4326)'.format(geom_colname='the_geom', geom_type=geom_type)

        create_query = '''CREATE TABLE {table_name} ({cols})'''.format(table_name=self._table_name, cols=cols)
        return create_query

    def _get_read_query(self, table_columns, limit=None):
        """Create the read (COPY TO) query"""
        query_columns = [column.name for column in table_columns if column.name != 'the_geom_webmercator']

        if self._query is not None:
            query = 'SELECT {columns} FROM ({query}) _q'.format(
                query=self._query,
                columns=', '.join(query_columns))
        else:
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



    def get_table_column_names(self, exclude=None):
        """Get column names and types from a table"""
        columns = [c.name for c in self.get_table_columns()]

        if exclude and isinstance(exclude, list):
            columns = list(set(columns) - set(exclude))

        return columns

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        if self._state == Dataset.STATE_REMOTE:
            return self._get_remote_geom_type()
        elif self._state == Dataset.STATE_LOCAL:
            return self._get_local_geom_type()

    def _get_remote_geom_type(self):
        """Fetch geom type of a remote table"""
        if self._con:
            response = self._client.execute_query('''
                SELECT distinct ST_GeometryType(the_geom) AS geom_type
                FROM ({}) q
                LIMIT 5
            '''.format(self.get_query()))
            if response and response.get('rows') and len(response.get('rows')) > 0:
                st_geom_type = response.get('rows')[0].get('geom_type')
                if st_geom_type:
                    return self._map_geom_type(st_geom_type[3:])

    def _get_local_geom_type(self):
        """Compute geom type of the local dataframe"""
        if not self._df.empty and 'geometry' in self._df and len(self._df.geometry) > 0:
            geometry = _first_value(self._df.geometry)
            if geometry and geometry.geom_type:
                return self._map_geom_type(geometry.geom_type)

    def _map_geom_type(self, geom_type):
        return {
            'Point': Dataset.GEOM_TYPE_POINT,
            'MultiPoint': Dataset.GEOM_TYPE_POINT,
            'LineString': Dataset.GEOM_TYPE_LINE,
            'MultiLineString': Dataset.GEOM_TYPE_LINE,
            'Polygon': Dataset.GEOM_TYPE_POLYGON,
            'MultiPolygon': Dataset.GEOM_TYPE_POLYGON
        }[geom_type]

    def _get_dataset_info(self):
        return DatasetInfo(self._con, self._table_name)



    def _get_schema(self):
        if self._con:
            return self._con.get_default_schema()
        else:
            return None




def _save_index_as_column(df):
    index_name = df.index.name
    if index_name is not None:
        if index_name not in df.columns:
            df.reset_index(inplace=True)
            df.set_index(index_name, drop=False, inplace=True)





def _dtypes2pg(dtype):
    """Returns equivalent PostgreSQL type for input `dtype`"""
    mapping = {
        'float64': 'numeric',
        'int64': 'integer',
        'float32': 'numeric',
        'int32': 'integer',
        'object': 'text',
        'bool': 'boolean',
        'datetime64[ns]': 'timestamp',
        'datetime64[ns, UTC]': 'timestamp',
    }
    return mapping.get(str(dtype), 'text')





def _get_geom_col_type(df):
    geom_col = _get_geom_col_name(df)
    if geom_col is not None:
        first_geom = _first_value(df[geom_col])
        if first_geom:
            enc_type = detect_encoding_type(first_geom)
            geom = decode_geometry(first_geom, enc_type)
            if geom is not None:
                return geom.geom_type
        else:
            warn('Dataset with null geometries')


def _first_value(array):
    array = array.loc[~array.isnull()]  # Remove null values
    if len(array) > 0:
        return array.iloc[0]



