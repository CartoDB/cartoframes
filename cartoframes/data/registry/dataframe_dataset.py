import pandas as pd
from warnings import warn
from tqdm import tqdm

from carto.exceptions import CartoException, CartoRateLimitException

from .base_dataset import BaseDataset
from ..columns import Column, normalize_names
from ..utils import decode_geometry, compute_geodataframe, \
    detect_encoding_type, save_index_as_column
from ...utils import map_geom_type, load_geojson, is_geojson


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

        normalized_column_names = _normalize_column_names(self._df)

        if if_exists == BaseDataset.REPLACE or not self.exists():
            self._create_table(normalized_column_names, with_lnglat)
        elif if_exists == BaseDataset.FAIL:
            raise self._already_exists_error()

        self._copyfrom(normalized_column_names, with_lnglat)

    def delete(self):
        raise ValueError('Method not allowed in DataFrameDataset. You should use a TableDataset: `Dataset(my_table)`')

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        return self._get_geom_type()

    def _copyfrom(self, normalized_column_names, with_lnglat):
        geom_col = _get_geom_col_name(self._df)
        enc_type = _detect_encoding_type(self._df, geom_col)

        columns_normalized = []
        columns_origin = [geom_col]
        for norm, orig in normalized_column_names:
            columns_normalized.append(norm)
            columns_origin.append(orig)
        columns_normalized.append('the_geom')

        query = """COPY {table_name}({columns}) FROM stdin WITH (FORMAT csv, DELIMITER '|');""".format(
            table_name=self._table_name,
            columns=','.join(columns_normalized))

        data = _rows(
            self._df,
            columns_origin,
            with_lnglat,
            geom_col,
            enc_type)

        self._context.upload(query, data)

    def _create_table(self, normalized_column_names, with_lnglat=None):
        query = '''BEGIN; {drop}; {create}; {cartodbfy}; COMMIT;'''.format(
            drop=self._drop_table_query(),
            create=self._create_table_query(normalized_column_names, with_lnglat),
            cartodbfy=self._cartodbfy_query())

        try:
            self._context.execute_long_running_query(query)
        except CartoRateLimitException as err:
            raise err
        except CartoException as err:
            raise CartoException('Cannot create table: {}.'.format(err))

    def _create_table_query(self, normalized_column_names, with_lnglat=None):
        if with_lnglat is None:
            geom_type = _get_geom_col_type(self._df)
        else:
            geom_type = 'Point'

        col = ('{col} {ctype}')
        cols = ', '.join(col.format(col=norm,
                                    ctype=_dtypes2pg(self._df.dtypes[orig]))
                         for norm, orig in normalized_column_names)

        if geom_type:
            cols += ', {geom_colname} geometry({geom_type}, 4326)'.format(geom_colname='the_geom', geom_type=geom_type)

        create_query = '''CREATE TABLE {table_name} ({cols})'''.format(table_name=self._table_name, cols=cols)
        return create_query

    def _get_geom_type(self):
        """Compute geom type of the local dataframe"""
        if not self._df.empty and 'geometry' in self._df and len(self._df.geometry) > 0:
            geometry = _first_value(self._df.geometry)
            if geometry and geometry.geom_type:
                return map_geom_type(geometry.geom_type)


def _rows(df, cols, with_lnglat, geom_col, enc_type):
    for i, row in df.iterrows():
        row_data = []
        the_geom_val = None
        lng_val = None
        lat_val = None
        for col in cols:
            val = row[col]
            if _is_null(val):
                val = ''
            if with_lnglat:
                if col == with_lnglat[0]:
                    lng_val = row[col]
                if col == with_lnglat[1]:
                    lat_val = row[col]
            if col == geom_col:
                the_geom_val = row[col]
            else:
                row_data.append('{}'.format(val))

        if the_geom_val is not None:
            geom = decode_geometry(the_geom_val, enc_type)
            if geom:
                row_data.append('SRID=4326;{geom}'.format(geom=geom.wkt))

        if len(row_data) < len(cols) and with_lnglat is not None and lng_val is not None and lat_val is not None:
            row_data.append('SRID=4326;POINT({lng} {lat})'.format(lng=lng_val, lat=lat_val))

        if len(row_data) < len(cols):
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


def _detect_encoding_type(df, geom_col):
    if geom_col is not None:
        first_geom = _first_value(df[geom_col])
        if first_geom:
            return detect_encoding_type(first_geom)
    return ''


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
