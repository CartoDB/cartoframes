import pandas as pd
from warnings import warn
from tqdm import tqdm

from carto.exceptions import CartoException, CartoRateLimitException

from .base_dataset import BaseDataset
from ....utils.columns import DataframeColumnsInfo, _first_value
from ....utils.geom_utils import decode_geometry, compute_geodataframe, save_index_as_column
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

        dataframeColumnsInfo = DataframeColumnsInfo(self._df, with_lnglat)

        if if_exists == BaseDataset.REPLACE or not self.exists():
            self._create_table(columns)
        elif if_exists == BaseDataset.FAIL:
            raise self._already_exists_error()

        self._copyfrom(columns, geom_column, enc_type, with_lnglat)

    def delete(self):
        raise ValueError('Method not allowed in DataFrameDataset. You should use a TableDataset: `Dataset(my_table)`')

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        return self._get_geom_type()

    def _copyfrom(self, columns, geom_column, enc_type, with_lnglat):
        query = """COPY {table_name}({columns}) FROM stdin WITH (FORMAT csv, DELIMITER '|');""".format(
            table_name=self._table_name,
            columns=','.join(c['database'] for c in columns))

        data = _rows(self._df, columns, geom_column, enc_type, with_lnglat)

        self._context.upload(query, data)

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


def _rows(df, columns, geom_column, enc_type, with_lnglat):
    for i, row in df.iterrows():
        row_data = []
        for c in columns:
            col = c['dataframe']
            if col not in df.columns:  # we could have filtered columns in the df. See _process_columns
                continue
            val = row[col]

            if _is_null(val):
                val = ''

            if geom_column and col == geom_column:
                geom = decode_geometry(val, enc_type)
                if geom:
                    row_data.append('SRID=4326;{}'.format(geom.wkt))
                else:
                    row_data.append('')
            else:
                row_data.append('{}'.format(val))

        if with_lnglat:
            lng_val = row[with_lnglat[0]]
            lat_val = row[with_lnglat[1]]
            if lng_val and lat_val:
                row_data.append('SRID=4326;POINT ({lng} {lat})'.format(lng=lng_val, lat=lat_val))
            else:
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
