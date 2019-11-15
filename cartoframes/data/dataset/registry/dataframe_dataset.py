from __future__ import absolute_import

import pandas as pd
from carto.exceptions import CartoException, CartoRateLimitException
from tqdm import tqdm

from ....utils.columns import DataframeColumnsInfo, _first_value
from ....utils.geom_utils import (compute_geodataframe, decode_geometry,
                                  save_index_as_column)
from ....utils.utils import is_geojson, load_geojson, map_geom_type, encode_row, PG_NULL
from .base_dataset import BaseDataset

# avoid _lock issue: https://github.com/tqdm/tqdm/issues/457
tqdm(disable=True, total=0)  # initialise internal lock


class DataFrameDataset(BaseDataset):
    def __init__(self, data, credentials=None, schema=None):
        super(DataFrameDataset, self).__init__()

        self._df = data

    @staticmethod
    def can_work_with(data, credentials):
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

        self._rename_index_for_upload()

        dataframe_columns_info = DataframeColumnsInfo(self._df, with_lnglat)

        if if_exists == BaseDataset.IF_EXISTS_REPLACE or not self.exists():
            self._create_table(dataframe_columns_info.columns)
        elif if_exists == BaseDataset.IF_EXISTS_FAIL:
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

    def get_num_rows(self):
        """Get the number of rows in the dataframe"""
        return len(self._df.index)

    def _copyfrom(self, dataframe_columns_info, with_lnglat):
        query = """
            COPY {table_name}({columns}) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '{null}');
        """.format(
            table_name=self._table_name, null=PG_NULL,
            columns=','.join(c.database for c in dataframe_columns_info.columns)).strip()

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
        return None

    def _rename_index_for_upload(self):
        if self._df.index.name != 'cartodb_id':
            if 'cartodb_id' not in self._df:
                if _is_valid_index_for_cartodb_id(self._df.index):
                    # rename a integer unnamed index to cartodb_id
                    self._df.index.rename('cartodb_id', inplace=True)
            else:
                if self._df.index.name is None:
                    # replace an unnamed index by a cartodb_id column
                    self._df.set_index('cartodb_id')


def _is_valid_index_for_cartodb_id(index):
    return index.name is None and index.nlevels == 1 and index.dtype == 'int' and index.is_unique


def _rows(df, dataframe_columns_info, with_lnglat):
    for index, _ in df.iterrows():
        row_data = []
        for c in dataframe_columns_info.columns:
            col = c.dataframe
            if col not in df.columns:
                if df.index.name and col == df.index.name:
                    val = index
                else:  # we could have filtered columns in the df. See DataframeColumnsInfo
                    continue
            else:
                val = df.at[index, col]

            if dataframe_columns_info.geom_column and col == dataframe_columns_info.geom_column:
                geom = decode_geometry(val, dataframe_columns_info.enc_type)
                if geom:
                    val = 'SRID=4326;{}'.format(geom.wkt)
                else:
                    val = ''

            row_data.append(encode_row(val))

        if with_lnglat:
            lng_val = df.at[index, with_lnglat[0]]
            lat_val = df.at[index, with_lnglat[1]]
            if lng_val is not None and lat_val is not None:
                val = 'SRID=4326;POINT ({lng} {lat})'.format(lng=lng_val, lat=lat_val)
            else:
                val = ''
            row_data.append(encode_row(val))

        csv_row = b'|'.join(row_data)
        csv_row += b'\n'

        yield csv_row
