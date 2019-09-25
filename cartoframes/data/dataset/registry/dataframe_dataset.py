import pandas as pd
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

        dataframe_columns_info = DataframeColumnsInfo(self._df, with_lnglat)

        if if_exists == BaseDataset.REPLACE or not self.exists():
            self._create_table(dataframe_columns_info.columns)
        elif if_exists == BaseDataset.FAIL:
            raise self._already_exists_error()

        self._copyfrom(dataframe_columns_info, with_lnglat)

    def delete(self):
        raise ValueError('Method not allowed in DataFrameDataset. You should use a TableDataset: `Dataset(my_table)`')

    def compute_geom_type(self):
        """Compute the geometry type from the data"""
        return self._get_geom_type()

    def get_column_names(self, exclude=None):
        """Get column names"""
        columns = list(self.dataframe.columns)
        if self.dataframe.index.name is not None and self.dataframe.index.name not in columns:
            columns.append(self.dataframe.index.name)

        if exclude and isinstance(exclude, list):
            columns = list(set(columns) - set(exclude))

        return columns

    def _copyfrom(self, dataframe_columns_info, with_lnglat):
        query = """COPY {table_name}({columns}) FROM stdin WITH (FORMAT csv, DELIMITER '|');""".format(
            table_name=self._table_name,
            columns=','.join(c.database for c in dataframe_columns_info.columns))

        data = _rows(self._df, dataframe_columns_info, with_lnglat)

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
        cols = ['{column} {type}'.format(column=c.database, type=c.database_type) for c in columns]

        return '''CREATE TABLE {table_name} ({cols})'''.format(
            table_name=self._table_name,
            cols=', '.join(cols))

    def _get_geom_type(self):
        """Compute geom type of the local dataframe"""
        if not self._df.empty and 'geometry' in self._df and len(self._df.geometry) > 0:
            geometry = _first_value(self._df.geometry)
            if geometry and geometry.geom_type:
                return map_geom_type(geometry.geom_type)


def _rows(df, dataframe_columns_info, with_lnglat):
    for i, row in df.iterrows():
        row_data = []
        for c in dataframe_columns_info.columns:
            col = c.dataframe
            if col not in df.columns:  # we could have filtered columns in the df. See DataframeColumnsInfo
                continue
            val = row[col]

            if _is_null(val):
                val = ''

            if dataframe_columns_info.geom_column and col == dataframe_columns_info.geom_column:
                geom = decode_geometry(val, dataframe_columns_info.enc_type)
                if geom:
                    val = 'SRID=4326;{}'.format(geom.wkt)
                else:
                    val = ''
            row_data.append(_encoded(val))

        if with_lnglat:
            lng_val = row[with_lnglat[0]]
            lat_val = row[with_lnglat[1]]
            if lng_val and lat_val:
                val = 'SRID=4326;POINT ({lng} {lat})'.format(lng=lng_val, lat=lat_val)
            else:
                val = ''
            row_data.append(_encoded(val))

        csv_row = _encoded('|').join(row_data)
        csv_row += _encoded('\n')

        yield csv_row


def _encoded(val):
    if isinstance(val, type(u'')):
        return val.encode('utf-8')
    elif isinstance(val, type(b'')):
        return val
    else:
        return u'{}'.format(val).encode('utf-8')


def _is_null(val):
    vnull = pd.isnull(val)
    if isinstance(vnull, bool):
        return vnull
    else:
        return vnull.all()
