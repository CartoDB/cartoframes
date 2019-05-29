import time
import pandas as pd
import binascii as ba

from tqdm import tqdm
from warnings import warn

from .columns import Column, normalize_names, normalize_name
from .geojson import load_geojson

from carto.exceptions import CartoException, CartoRateLimitException

# avoid _lock issue: https://github.com/tqdm/tqdm/issues/457
tqdm(disable=True, total=0)  # initialise internal lock


class Dataset(object):
    FAIL = 'fail'
    REPLACE = 'replace'
    APPEND = 'append'

    PRIVATE = 'private'
    PUBLIC = 'public'
    LINK = 'link'

    STATE_LOCAL = 'local'
    STATE_REMOTE = 'remote'

    GEOM_TYPE_POINT = 'point'
    GEOM_TYPE_LINE = 'line'
    GEOM_TYPE_POLYGON = 'polygon'

    DEFAULT_RETRY_TIMES = 3

    def __init__(self, table_name=None, schema=None, query=None, df=None, gdf=None, state=None, context=None):
        from .auth import _default_context
        self.cc = context or _default_context

        self.table_name = normalize_name(table_name)
        self.schema = schema or self._get_schema()
        self.query = query
        self.df = df
        self.gdf = gdf

        if not self._validate_init():
            raise ValueError('Wrong Dataset creation. You should use one of the class methods: '
                             'from_table, from_query, from_dataframe, from_geodataframe, from_geojson')

        self.state = state
        self.normalized_column_names = None

        if self.table_name != table_name:
            warn('Table will be named `{}`'.format(table_name))

    @classmethod
    def from_table(cls, table_name, context=None, schema=None):
        return cls(table_name=table_name, schema=schema, context=context, state=cls.STATE_REMOTE)

    @classmethod
    def from_query(cls, query, context=None):
        return cls(query=query, context=context, state=cls.STATE_REMOTE)

    @classmethod
    def from_dataframe(cls, df):
        dataset = cls(df=df, state=cls.STATE_LOCAL)
        _save_index_as_column(dataset.df)
        return dataset

    @classmethod
    def from_geodataframe(cls, gdf):
        dataset = cls(gdf=gdf, state=cls.STATE_LOCAL)
        _save_index_as_column(dataset.gdf)
        return dataset

    @classmethod
    def from_geojson(cls, geojson):
        return cls(gdf=load_geojson(geojson), state=cls.STATE_LOCAL)

    def upload(self, with_lnglat=None, if_exists=FAIL, table_name=None, schema=None, context=None):
        if table_name:
            self.table_name = normalize_name(table_name)
        if schema:
            self.schema = schema
        if context:
            self.cc = context

        if self.table_name is None or self.cc is None:
            raise ValueError('You should provide a table_name and context to upload data.')

        if self.gdf is None and self.df is None and self.query is None:
            raise ValueError('Nothing to upload.'
                             'We need data in a DataFrame or GeoDataFrame or a query to upload data to CARTO.')

        already_exists_error = CartoException('Table with name {t} and schema {s} already exists in CARTO.'
                                              'Please choose a different `table_name` or use'
                                              'if_exists="replace" to overwrite it'.format(
                                                  t=self.table_name, s=self.schema))

        # priority order: gdf, df, query
        if self.gdf is not None:
            warn('GeoDataFrame option is still under development. We will try the upload with DataFrame')
            # TODO: uncomment when we support GeoDataFrame
            # self.normalized_column_names = _normalize_column_names(self.gdf)

        if self.df is not None:
            self.normalized_column_names = _normalize_column_names(self.df)

            if if_exists == Dataset.REPLACE or not self.exists():
                self._create_table(with_lnglat)
            elif if_exists == Dataset.FAIL:
                raise already_exists_error

            self._copyfrom(with_lnglat)

        elif self.query is not None:
            if if_exists == Dataset.APPEND:
                raise CartoException('Error using append with a query Dataset.'
                                     'It is not possible to append data to a query')
            elif if_exists == Dataset.REPLACE or not self.exists():
                self._create_table_from_query()
            elif if_exists == Dataset.FAIL:
                raise already_exists_error

        return self

    def download(self, limit=None, decode_geom=False, retry_times=DEFAULT_RETRY_TIMES):
        if self.cc is None or (self.table_name is None and self.query is None):
            raise ValueError('You should provide a context and a table_name or query to download data.')

        # priority order: query, table
        table_columns = self.get_table_columns()
        query = self._get_read_query(table_columns, limit)
        self.df = self.cc.fetch(query, decode_geom=decode_geom)
        return self.df

    def delete(self):
        if self.exists():
            self.cc.sql_client.send(self._drop_table_query(False))
            return True

        return False

    def exists(self):
        """Checks to see if table exists"""
        try:
            self.cc.sql_client.send(
                'EXPLAIN SELECT * FROM "{table_name}"'.format(
                    table_name=self.table_name),
                do_post=False)
            return True
        except CartoException as err:
            # If table doesn't exist, we get an error from the SQL API
            self.cc._debug_print(err=err)
            return False

    def _create_table(self, with_lnglat=None):
        job = self.cc.batch_sql_client \
                  .create_and_wait_for_completion(
                      '''BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'''
                      .format(drop=self._drop_table_query(),
                              create=self._create_table_query(with_lnglat),
                              cartodbfy=self._cartodbfy_query()))

        if job['status'] != 'done':
            raise CartoException('Cannot create table: {}.'.format(job['failed_reason']))

    def _validate_init(self):
        inputs = [self.table_name, self.query, self.df, self.gdf]
        inputs_number = sum(x is not None for x in inputs)

        if inputs_number != 1:
            return False

        return True

    def _cartodbfy_query(self):
        return "SELECT CDB_CartodbfyTable('{schema}', '{table_name}')" \
            .format(schema=self.schema or self.cc.get_default_schema(), table_name=self.table_name)

    def _copyfrom(self, with_lnglat=None):
        geom_col = _get_geom_col_name(self.df)

        columns = ','.join(norm for norm, orig in self.normalized_column_names)
        self.cc.copy_client.copyfrom(
            """COPY {table_name}({columns},the_geom)
               FROM stdin WITH (FORMAT csv, DELIMITER '|');""".format(table_name=self.table_name, columns=columns),
            self._rows(self.df, [c for c in self.df.columns if c != 'cartodb_id'], with_lnglat, geom_col)
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
                if pd.isnull(val) or val is None:
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
                geom = _decode_geom(the_geom_val)
                if geom:
                    csv_row += 'SRID=4326;{geom}'.format(geom=geom.wkt)
            if with_lnglat is not None and lng_val is not None and lat_val is not None:
                csv_row += 'SRID=4326;POINT({lng} {lat})'.format(lng=lng_val, lat=lat_val)

            csv_row += '\n'
            yield csv_row.encode()

    def _drop_table_query(self, if_exists=True):
        return '''DROP TABLE {if_exists} {table_name}'''.format(
            table_name=self.table_name,
            if_exists='IF EXISTS' if if_exists else '')

    def _create_table_from_query(self):
        self.cc.batch_sql_client.create_and_wait_for_completion(
            '''BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'''
            .format(drop=self._drop_table_query(),
                    create=self._get_query_to_create_table_from_query(),
                    cartodbfy=self._cartodbfy_query()))

    def _get_query_to_create_table_from_query(self):
        return '''CREATE TABLE {table_name} AS ({query})'''.format(table_name=self.table_name, query=self.query)

    def _create_table_query(self, with_lnglat=None):
        if with_lnglat is None:
            geom_type = _get_geom_col_type(self.df)
        else:
            geom_type = 'Point'

        col = ('{col} {ctype}')
        cols = ', '.join(col.format(col=norm,
                                    ctype=_dtypes2pg(self.df.dtypes[orig]))
                         for norm, orig in self.normalized_column_names)

        if geom_type:
            cols += ', {geom_colname} geometry({geom_type}, 4326)'.format(geom_colname='the_geom', geom_type=geom_type)

        create_query = '''CREATE TABLE {table_name} ({cols})'''.format(table_name=self.table_name, cols=cols)
        return create_query

    def _get_read_query(self, table_columns, limit=None):
        """Create the read (COPY TO) query"""
        query_columns = [column.name for column in table_columns if column.name != 'the_geom_webmercator']

        if self.query is not None:
            query = 'SELECT {columns} FROM ({query}) _q'.format(
                query=self.query,
                columns=', '.join(query_columns))
        else:
            query = 'SELECT {columns} FROM "{schema}"."{table_name}"'.format(
                table_name=self.table_name,
                schema=self.schema,
                columns=', '.join(query_columns))

        if limit is not None:
            if isinstance(limit, int) and (limit >= 0):
                query += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")

        return query

    def get_table_columns(self):
        """Get column names and types from a table or query result"""
        if self.query is not None:
            query = 'SELECT * FROM ({}) _q limit 0'.format(self.query)
            return get_columns(self.cc, query)
        else:
            query = '''
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table}' AND table_schema = '{schema}'
            '''.format(table=self.table_name, schema=self.schema)

            try:
                table_info = self.cc.sql_client.send(query)
                return [Column(c['column_name'], pgtype=c['data_type']) for c in table_info['rows']]
            except CartoException as e:
                # this may happen when using the default_public API key
                if str(e) == 'Access denied':
                    query = '''
                        SELECT *
                        FROM "{schema}"."{table}" LIMIT 0
                    '''.format(table=self.table_name, schema=self.schema)
                    return get_columns(self.cc, query)
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
        if self.state == Dataset.STATE_REMOTE:
            return self._get_remote_geom_type(get_query(self))
        elif self.state == Dataset.STATE_LOCAL:
            return self._get_local_geom_type(self.gdf)

    def _get_remote_geom_type(self, query):
        """Fetch geom type of a remote table"""
        if self.cc:
            response = self.cc.sql_client.send('''
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
            geom_type = gdf.geometry[0].type
            if geom_type:
                return self._map_geom_type(geom_type)

    def _map_geom_type(self, geom_type):
        return {
            'Point': Dataset.GEOM_TYPE_POINT,
            'MultiPoint': Dataset.GEOM_TYPE_POINT,
            'LineString': Dataset.GEOM_TYPE_LINE,
            'MultiLineString': Dataset.GEOM_TYPE_LINE,
            'Polygon': Dataset.GEOM_TYPE_POLYGON,
            'MultiPolygon': Dataset.GEOM_TYPE_POLYGON
        }[geom_type]

    def _get_schema(self):
        if self.cc:
            return self.cc.get_default_schema()
        else:
            return 'public'


def recursive_read(context, query, retry_times=Dataset.DEFAULT_RETRY_TIMES):
    try:
        return context.copy_client.copyto_stream(query)
    except CartoRateLimitException as err:
        if retry_times > 0:
            retry_times -= 1
            warn('Read call rate limited. Waiting {s} seconds'.format(s=err.retry_after))
            time.sleep(err.retry_after)
            warn('Retrying...')
            return recursive_read(context, query, retry_times=retry_times)
        else:
            warn(('Read call was rate-limited. '
                  'This usually happens when there are multiple queries being read at the same time.'))
            raise err


def get_columns(context, query):
    col_query = '''SELECT * FROM ({query}) _q LIMIT 0'''.format(query=query)
    table_info = context.sql_client.send(col_query)
    return Column.from_sql_api_fields(table_info['fields'])


def get_query(dataset):
    if isinstance(dataset, Dataset):
        return dataset.query or _default_query(dataset)


def _default_query(dataset):
    if dataset.table_name and dataset.schema:
        return 'SELECT * FROM "{0}"."{1}"'.format(dataset.schema, dataset.table_name)


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
    if geom_col is None:
        return None

    try:
        geom = _decode_geom(_first_not_null_value(df, geom_col))
    except IndexError:
        warn('Dataset with null geometries')
        geom = None

    if geom is None:
        return None

    return geom.geom_type


def _first_not_null_value(df, col):
    return df[col].loc[~df[col].isnull()].iloc[0]


def _encode_decode_decorator(func):
    """decorator for encoding and decoding geoms"""
    def wrapper(*args):
        """error catching"""
        try:
            processed_geom = func(*args)
            return processed_geom
        except ImportError as err:
            raise ImportError('The Python package `shapely` needs to be '
                              'installed to encode or decode geometries. '
                              '({})'.format(err))
    return wrapper


@_encode_decode_decorator
def _decode_geom(ewkb):
    """Decode encoded wkb into a shapely geometry
    """
    # it's already a shapely object
    if hasattr(ewkb, 'geom_type'):
        return ewkb

    from shapely import wkb
    from shapely import wkt
    if ewkb:
        try:
            return wkb.loads(ba.unhexlify(ewkb))
        except Exception:
            try:
                return wkb.loads(ba.unhexlify(ewkb), hex=True)
            except Exception:
                try:
                    return wkb.loads(ewkb, hex=True)
                except Exception:
                    try:
                        return wkb.loads(ewkb)
                    except Exception:
                        try:
                            return wkt.loads(ewkb)
                        except Exception:
                            pass
    return None
