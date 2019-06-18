"""Dataset
======="""
import pandas as pd
from tqdm import tqdm
from warnings import warn

from carto.exceptions import CartoException

from .utils import decode_geometry, compute_query, compute_geodataframe, get_columns, DEFAULT_RETRY_TIMES, \
    get_public_context
from .dataset_info import DatasetInfo
from ..columns import Column, normalize_names, normalize_name
from ..geojson import load_geojson

# avoid _lock issue: https://github.com/tqdm/tqdm/issues/457
tqdm(disable=True, total=0)  # initialise internal lock


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

    def __init__(self, table_name=None, schema=None,
                 query=None, df=None, gdf=None,
                 state=None, is_saved_in_carto=False, context=None):
        from ..auth import _default_context
        self._cc = context or _default_context

        self._table_name = normalize_name(table_name)
        self._schema = schema or self._get_schema()
        self._query = query
        self._df = df
        self._gdf = gdf

        if not self._validate_init():
            raise ValueError('Improper dataset creation. You should use one of the class methods: '
                             'from_table, from_query, from_dataframe, from_geodataframe, from_geojson')

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
        dataset = cls(gdf=gdf, state=cls.STATE_LOCAL)
        _save_index_as_column(dataset._gdf)
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
        return cls(gdf=load_geojson(geojson), state=cls.STATE_LOCAL)

    @property
    def dataframe(self):
        """Dataset DataFrame"""
        return self._df

    @property
    def geodataframe(self):
        """Dataset GeoDataFrame"""
        return self._gdf

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

    @property
    def context(self):
        """Dataset :py:class:`Context <cartoframes.auth.Context>`"""
        return self._cc

    @context.setter
    def context(self, context):
        """Set a new :py:class:`Context <cartoframes.auth.Context>` for a Dataset instance."""
        self._cc = context
        self._schema = context.get_default_schema()

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

               d = Dataset.from_table('tablename')
               d.dataset_info

        """
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

    def upload(self, with_lnglat=None, if_exists=FAIL, table_name=None, schema=None, context=None):
        """Upload Dataset to CARTO account associated with `context`.

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
            context (:py:class:`Context <cartoframes.auth.Context>`, optional):
              Context of user account to send Dataset to. If not provided,
              a default context (if set with :py:meth:`set_default_context
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
                d = Dataset.from_dataframe(df)
                d.upload(with_lnglat=('lng', 'lat'), table_name='sample_table')

        """
        if table_name:
            self._table_name = normalize_name(table_name)
        if context:
            self.context = context
        if schema:
            self._schema = schema

        if self._table_name is None or self._cc is None:
            raise ValueError('You should provide a table_name and context to upload data.')

        if self._gdf is None and self._df is None and self._query is None:
            raise ValueError('Nothing to upload. Dataset needs a DataFrame, a '
                             'GeoDataFrame, or a query to upload data to CARTO.')

        already_exists_error = CartoException('Table with name {t} and schema {s} already exists in CARTO.'
                                              'Please choose a different `table_name` or use '
                                              'if_exists="replace" to overwrite it'.format(
                                                  t=self._table_name, s=self._schema))

        # priority order: gdf, df, query
        if self._gdf is not None:
            warn('GeoDataFrame option is still under development. Attempting '
                 'to upload as a DataFrame')
            # TODO: uncomment when we support GeoDataFrame
            # self._normalized_column_names = _normalize_column_names(self._gdf)

        if self._df is not None:
            self._normalized_column_names = _normalize_column_names(self._df)

            if if_exists == Dataset.REPLACE or not self.exists():
                self._create_table(with_lnglat)
                if if_exists != Dataset.APPEND:
                    self._is_saved_in_carto = True
            elif if_exists == Dataset.FAIL:
                raise already_exists_error

            self._copyfrom(with_lnglat)

        elif self._query is not None:
            if if_exists == Dataset.APPEND:
                raise CartoException('Error using append with a query Dataset.'
                                     'It is not possible to append data to a query')
            elif if_exists == Dataset.REPLACE or not self.exists():
                self._create_table_from_query()
                self._is_saved_in_carto = True
            elif if_exists == Dataset.FAIL:
                raise already_exists_error

        return self

    def download(self, limit=None, decode_geom=False, retry_times=DEFAULT_RETRY_TIMES):
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
              in case it fails. Default is Dataset.DEFAULT_RETRY_TIMES.


        Example:

            .. code::

                from cartoframes.data import Dataset
                from cartoframes.auth import set_default_context

                # use cartoframes example account
                set_default_context('https://cartoframes.carto.com')

                d = Dataset('brooklyn_poverty')

                df = d.download(decode_geom=True)

        """
        if self._cc is None or (self._table_name is None and self._query is None):
            raise ValueError('You should provide a context and a table_name or query to download data.')

        # priority order: query, table
        table_columns = self.get_table_columns()
        query = self._get_read_query(table_columns, limit)
        self._df = self._cc.fetch(query, decode_geom=decode_geom)
        return self._df

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
            self._cc.sql_client.send(self._drop_table_query(False))
            self._unsync()
            return True

        return False

    def exists(self):
        """Checks to see if table exists"""
        try:
            self._cc.sql_client.send(
                'EXPLAIN SELECT * FROM "{table_name}"'.format(table_name=self._table_name),
                do_post=False)
            return True
        except CartoException as err:
            # If table doesn't exist, we get an error from the SQL API
            self._cc._debug_print(err=err)
            return False

    def is_public(self):
        """Checks to see if table or table used by query has public privacy"""
        public_context = get_public_context(self.context)
        try:
            public_context.sql_client.send('EXPLAIN {}'.format(get_query(self)), do_post=False)
            return True
        except CartoException:
            return False

    def _create_table(self, with_lnglat=None):
        job = self._cc.batch_sql_client \
                  .create_and_wait_for_completion(
                      '''BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'''
                      .format(drop=self._drop_table_query(),
                              create=self._create_table_query(with_lnglat),
                              cartodbfy=self._cartodbfy_query()))

        if job['status'] != 'done':
            raise CartoException('Cannot create table: {}.'.format(job['failed_reason']))

    def _validate_init(self):
        inputs = [self._table_name, self._query, self._df, self._gdf]
        inputs_number = sum(x is not None for x in inputs)

        if inputs_number != 1:
            return False

        return True

    def _cartodbfy_query(self):
        return "SELECT CDB_CartodbfyTable('{schema}', '{table_name}')" \
            .format(schema=self._schema or self._get_schema(), table_name=self._table_name)

    def _copyfrom(self, with_lnglat=None):
        geom_col = _get_geom_col_name(self._df)

        columns = ','.join(norm for norm, orig in self._normalized_column_names)
        self._cc.copy_client.copyfrom(
            """COPY {table_name}({columns},the_geom)
               FROM stdin WITH (FORMAT csv, DELIMITER '|');""".format(table_name=self._table_name, columns=columns),
            self._rows(self._df, [c for c in self._df.columns if c != 'cartodb_id'], with_lnglat, geom_col)
        )

    def _rows(self, df, cols, with_lnglat, geom_col):
        for i, row in df.iterrows():
            csv_row = ''
            the_geom_val = None
            lng_val = None
            lat_val = None
            for col in cols:
                if with_lnglat and col in Column.SUPPORTED_GEOM_COL_NAMES:
                    continue
                val = row[col]
                if self._is_null(val):
                    val = ''
                if with_lnglat:
                    if col == with_lnglat[0]:
                        lng_val = row[col]
                    if col == with_lnglat[1]:
                        lat_val = row[col]
                if col == geom_col:
                    the_geom_val = row[col]
                else:
                    csv_row += '{val}|'.format(val=val)

            if the_geom_val is not None:
                geom = decode_geometry(the_geom_val)
                if geom:
                    csv_row += 'SRID=4326;{geom}'.format(geom=geom.wkt)
            if with_lnglat is not None and lng_val is not None and lat_val is not None:
                csv_row += 'SRID=4326;POINT({lng} {lat})'.format(lng=lng_val, lat=lat_val)

            csv_row += '\n'
            yield csv_row.encode()

    def _is_null(self, val):
        vnull = pd.isnull(val)
        if isinstance(vnull, bool):
            return vnull
        else:
            return vnull.all()

    def _drop_table_query(self, if_exists=True):
        return '''DROP TABLE {if_exists} {table_name}'''.format(
            table_name=self._table_name,
            if_exists='IF EXISTS' if if_exists else '')

    def _create_table_from_query(self):
        self._cc.batch_sql_client.create_and_wait_for_completion(
            '''BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'''
                .format(drop=self._drop_table_query(),
                        create=self._get_query_to_create_table_from_query(),
                        cartodbfy=self._cartodbfy_query()))

    def _get_query_to_create_table_from_query(self):
        return '''CREATE TABLE {table_name} AS ({query})'''.format(table_name=self._table_name, query=self._query)

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

    def get_table_columns(self):
        """Get column names and types from a table or query result"""
        if self._query is not None:
            query = 'SELECT * FROM ({}) _q limit 0'.format(self._query)
            return get_columns(self._cc, query)
        else:
            query = '''
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table}' AND table_schema = '{schema}'
            '''.format(table=self._table_name, schema=self._schema)

            try:
                table_info = self._cc.sql_client.send(query)
                return [Column(c['column_name'], pgtype=c['data_type']) for c in table_info['rows']]
            except CartoException as e:
                # this may happen when using the default_public API key
                if str(e) == 'Access denied':
                    query = '''
                        SELECT *
                        FROM "{schema}"."{table}" LIMIT 0
                    '''.format(table=self._table_name, schema=self._schema)
                    return get_columns(self._cc, query)
                else:
                    raise e

    def get_table_column_names(self, exclude=None):
        """Get column names and types from a table"""
        columns = [c.name for c in self.get_table_columns()]

        if exclude and isinstance(exclude, list):
            columns = list(set(columns) - set(exclude))

        return columns

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        if self._state == Dataset.STATE_REMOTE:
            return self._get_remote_geom_type(get_query(self))
        elif self._state == Dataset.STATE_LOCAL:
            return self._get_local_geom_type(get_geodataframe(self))

    def _get_remote_geom_type(self, query):
        """Fetch geom type of a remote table"""
        if self._cc:
            response = self._cc.sql_client.send('''
                SELECT distinct ST_GeometryType(the_geom) AS geom_type
                FROM ({}) q
                LIMIT 5
            '''.format(query))
            if response and response.get('rows') and len(response.get('rows')) > 0:
                st_geom_type = response.get('rows')[0].get('geom_type')
                if st_geom_type:
                    return self._map_geom_type(st_geom_type[3:])

    def _get_local_geom_type(self, gdf):
        """Compute geom type of the local dataframe"""
        if len(gdf.geometry) > 0:
            geometry = _first_value(gdf.geometry)
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
        return DatasetInfo(self._cc, self._table_name)

    def _unsync(self):
        self._is_saved_in_carto = False
        self._dataset_info = None

    def _get_schema(self):
        if self._cc:
            return self._cc.get_default_schema()
        else:
            return None


def get_query(dataset):
    if isinstance(dataset, Dataset):
        if dataset.query is None:
            return compute_query(dataset)
        else:
            return dataset.query


def get_geodataframe(dataset):
    if isinstance(dataset, Dataset):
        if dataset.geodataframe is None:
            return compute_geodataframe(dataset)
        else:
            return dataset.geodataframe


def _save_index_as_column(df):
    index_name = df.index.name
    if index_name is not None:
        if index_name not in df.columns:
            df.reset_index(inplace=True)
            df.set_index(index_name, drop=False, inplace=True)


def _normalize_column_names(df):
    column_names = [c for c in df.columns if c not in Column.RESERVED_COLUMN_NAMES]
    normalized_columns = normalize_names(column_names)

    column_tuples = [(norm, orig) for orig, norm in zip(column_names, normalized_columns)]

    changed_cols = '\n'.join([
        '\033[1m{orig}\033[0m -> \033[1m{new}\033[0m'.format(
            orig=orig,
            new=norm)
        for norm, orig in column_tuples if norm != orig])

    if changed_cols != '':
        tqdm.write('The following columns were changed in the CARTO '
                   'copy of this dataframe:\n{0}'.format(changed_cols))

    return column_tuples


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


def _get_geom_col_name(df):
    geom_col = getattr(df, '_geometry_column_name', None)
    if geom_col is None:
        try:
            geom_col = next(x for x in df.columns if x.lower() in Column.SUPPORTED_GEOM_COL_NAMES)
        except StopIteration:
            pass

    return geom_col


def _get_geom_col_type(df):
    geom_col = _get_geom_col_name(df)
    if geom_col is not None:
        geom = decode_geometry(_first_value(df[geom_col]))
        if geom is not None:
            return geom.geom_type


def _first_value(array):
    array = array.loc[~array.isnull()]  # Remove null values
    if len(array) > 0:
        return array.iloc[0]
    else:
        warn('Dataset with null geometries')
