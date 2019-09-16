import pandas as pd
from warnings import warn
from tqdm import tqdm

from carto.exceptions import CartoException, CartoRateLimitException

from .base_dataset import BaseDataset
from ....utils.columns import Column, normalize_names, normalize_name
from ....utils.geom_utils import decode_geometry, compute_geodataframe, \
    detect_encoding_type, save_index_as_column
from ....utils.utils import map_geom_type, load_geojson, is_geojson


# avoid _lock issue: https://github.com/tqdm/tqdm/issues/457
tqdm(disable=True, total=0)  # initialise internal lock


class DataFrameDataset(BaseDataset):
    def __init__(self, data, credentials=None, schema=None):
        super(DataFrameDataset, self).__init__()

        self._df = data

    @staticmethod
    def can_work_with(data):
        return isinstance(data, pd.DataFrame) or is_geojson(data)

    @classmethod
    def create(cls, data, credentials=None, schema=None):
        if is_geojson(data):
            data = load_geojson(data)

        save_index_as_column(data)

        return cls(data)

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

    def download(self, limit, decode_geom, retry_times):
        self._is_ready_for_dowload_validation()

    def upload(self, if_exists, with_lnglat):
        self._is_ready_for_upload_validation()

        columns, geom_column, geometry = _process_columns(self._df, with_lnglat)

        if if_exists == BaseDataset.REPLACE or not self.exists():
            self._create_table(columns)
        elif if_exists == BaseDataset.FAIL:
            raise self._already_exists_error()

        self._copyfrom(columns, geom_column, geometry, with_lnglat)

    def delete(self):
        raise ValueError('Method not allowed in DataFrameDataset. You should use a TableDataset: `Dataset(my_table)`')

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        return self._get_geom_type()

    def _copyfrom(self, columns, geom_column, geometry, with_lnglat):
        query = """COPY {table_name}({columns}) FROM stdin WITH (FORMAT csv, DELIMITER '|');""".format(
            table_name=self._table_name,
            columns=','.join(c['database'] for c in columns))

        data = _rows(self._df, columns, geom_column, geometry, with_lnglat)

        self._context.upload(query, data)

    def _copyfrom_column_names(self, geom_col, normalized_column_names, with_lnglat=None):
        columns_normalized = []
        columns_origin = []

        if geom_col:
            columns_origin.append(geom_col)

        for norm, orig in normalized_column_names:
            columns_normalized.append(norm)
            columns_origin.append(orig)

        if geom_col or with_lnglat:
            columns_normalized.append('the_geom')

        return columns_normalized, columns_origin

    def _create_table(self, columns):
        query = '''BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'''.format(
            drop=self._drop_table_query(),
            create=self._create_table_query(columns),
            cartodbfy=self._cartodbfy_query())

        try:
            self._context.execute_long_running_query(query)
        except CartoRateLimitException as err:
            raise err
        except CartoException as err:
            raise CartoException('Cannot create table: {}.'.format(err))

    def _create_table_query(self, columns):
        cols = ['{column} {type}'.format(column=c['database'], type=c['database_type']) for c in columns]

        return '''CREATE TABLE {table_name} ({cols})'''.format(
            table_name=self._table_name,
            cols=', '.join(cols))

    def _get_geom_type(self):
        """Compute geom type of the local dataframe"""
        if not self._df.empty and 'geometry' in self._df and len(self._df.geometry) > 0:
            geometry = _first_value(self._df.geometry)
            if geometry and geometry.geom_type:
                return map_geom_type(geometry.geom_type)


def _rows(df, columns, geom_column, geometry, with_lnglat):
    for i, row in df.iterrows():
        row_data = []
        the_geom_val = None
        lng_val = None
        lat_val = None
        for c in columns:
            col = c['dataframe']
            val = row[col]
            if _is_null(val):
                val = ''
            if with_lnglat:
                if col == with_lnglat[0]:
                    lng_val = val
                if col == with_lnglat[1]:
                    lat_val = val
            if geom_column and col == geom_column:
                the_geom_val = val
            else:
                row_data.append('{}'.format(val))

        if the_geom_val is not None:
            row_data.append('SRID=4326;{}'.format(geometry.wkt))
        elif with_lnglat is not None and lng_val is not None and lat_val is not None:
            row_data.append('SRID=4326;POINT({lng} {lat})'.format(lng=lng_val, lat=lat_val))

        if len(row_data) < len(columns):
            row_data.append('')

        csv_row = '|'.join(row_data)
        csv_row += '\n'

        yield csv_row.encode()


def _is_null(val):
    vnull = pd.isnull(val)
    if isinstance(vnull, bool):
        return vnull
    else:
        return vnull.all()


def _process_columns(df, with_lnglat=None):
    geom_column = _get_geom_col_name(df)
    geometry = _get_geometry(df, geom_column)

    columns = [{
        'dataframe': c,
        'database': _database_column_name(c, geom_column),
        'database_type': _db_column_type(df, c, geom_column, geometry)
    } for c in df.columns]

    if geom_column is None and with_lnglat:
        columns.append({
            'dataframe': None,
            'database': 'the_geom',
            'database_type': 'geometry(Point, 4326)'
        })

    return columns, geom_column, geometry


def _database_column_name(column, geom_column):
    if geom_column and column == geom_column:
        normalized_name = 'the_geom'
    else:
        normalized_name = normalize_name(column)
        if normalized_name in Column.RESERVED_COLUMN_NAMES:
            normalized_name = normalized_name + '_1'

    return normalized_name


def _db_column_type(df, column, geom_column, geometry):  # TODO: detect geometries
    if geom_column and column == geom_column:
        db_type = 'geometry({}, 4326)'.format(geometry.geom_type)
    else:
        db_type = _dtypes2pg(df.dtypes[column])

    return db_type


def _dtypes2pg(dtype):
    """Returns equivalent PostgreSQL type for input `dtype`"""
    mapping = {
        'float64': 'numeric',
        'int64': 'bigint',
        'float32': 'numeric',
        'int32': 'integer',
        'object': 'text',
        'bool': 'boolean',
        'datetime64[ns]': 'timestamp',
        'datetime64[ns, UTC]': 'timestamp',
    }
    return mapping.get(str(dtype), 'text')


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


def _get_geom_col_name(df):
    geom_col = getattr(df, '_geometry_column_name', None)
    if geom_col is None:
        try:
            geom_col = next(x for x in df.columns if x.lower() in Column.SUPPORTED_GEOM_COL_NAMES)
        except StopIteration:
            pass

    return geom_col


def _detect_geometry_encoding_type(df, geom_col):
    if geom_col is not None:
        first_geom = _first_value(df[geom_col])
        if first_geom:
            return detect_encoding_type(first_geom)
    return ''


def _get_geometry(df, geom_col):
    if geom_col is not None:
        first_geom = _first_value(df[geom_col])
        if first_geom:
            enc_type = detect_encoding_type(first_geom)
            return decode_geometry(first_geom, enc_type)


def _first_value(series):
    series = series.loc[~series.isnull()]  # Remove null values
    if len(series) > 0:
        return series.iloc[0]
