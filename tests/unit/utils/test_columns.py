# coding=UTF-8

"""Unit tests for cartoframes.data.columns"""

from pandas import DataFrame
from geopandas import GeoDataFrame

from cartoframes.utils.geom_utils import set_geometry
from cartoframes.utils.columns import Column, ColumnInfo, get_dataframe_columns_info, normalize_names


class TestColumns(object):
    """Tests for functions in columns module"""

    def setup_method(self):
        self.cols = ['Unnamed: 0',
                     '201moore',
                     '201moore',
                     'Acadia 1.2.3',
                     'old_soaker',
                     '_testingTesting',
                     'test-1',
                     'test-1--2',
                     'test;',
                     'test,',
                     1,
                     1.0,
                     'public',
                     'SELECT',
                     'à',
                     'a',
                     '_a',
                     'longcolumnshouldbesplittedsomehowanditellyouwhereitsgonnabesplittedrightnow',
                     'longcolumnshouldbesplittedsomehowanditellyouwhereitsgonnabesplittedrightnow',
                     'all']
        self.cols_ans = ['unnamed_0',
                         '_201moore',
                         '_201moore_1',
                         'acadia_1_2_3',
                         'old_soaker',
                         '_testingtesting',
                         'test_1',
                         'test_1_2',
                         'test_',
                         'test__1',
                         '_1',
                         '_1_0',
                         'public',
                         '_select',
                         'a',
                         'a_1',
                         '_a',
                         'longcolumnshouldbesplittedsomehowanditellyouwhereitsgonnabespli',
                         'longcolumnshouldbesplittedsomehowanditellyouwhereitsgonnabe_1',
                         '_all']

    def test_normalize(self):
        other_cols = []
        for c, a in zip(self.cols, self.cols_ans):
            # changed cols should match answers
            column = Column(c)
            a_column = Column(a)
            column.normalize(other_cols)
            a_column.normalize(other_cols)
            assert column.name == a
            # already sql-normed cols should match themselves
            assert a_column.name == a
            other_cols.append(column.name)

    def test_normalize_names(self):
        assert normalize_names(self.cols) == self.cols_ans

    def test_normalize_names_unchanged(self):
        assert normalize_names(self.cols_ans) == self.cols_ans

    def test_column_info_with_geom(self):
        gdf = GeoDataFrame(
            [['Gran Vía 46', 'Madrid', 'POINT (0 0)'], ['Ebro 1', 'Sevilla', 'POINT (1 1)']],
            columns=['Address', 'City', 'the_geom'])
        set_geometry(gdf, 'the_geom', inplace=True)

        dataframe_columns_info = get_dataframe_columns_info(gdf)

        assert dataframe_columns_info == [
            ColumnInfo('Address', 'address', 'text', False),
            ColumnInfo('City', 'city', 'text', False),
            ColumnInfo('the_geom', 'the_geom', 'geometry(Point, 4326)', True)
        ]

    def test_column_info_without_geom(self):
        df = DataFrame(
            [['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']],
            columns=['Address', 'City']
        )

        dataframe_columns_info = get_dataframe_columns_info(df)

        assert dataframe_columns_info == [
            ColumnInfo('Address', 'address', 'text', False),
            ColumnInfo('City', 'city', 'text', False)
        ]

    def test_column_info_basic_troubled_names(self):
        gdf = GeoDataFrame(
            [[1, 'POINT (1 1)', 'fake_geom']],
            columns=['cartodb_id', 'the_geom', 'the_geom_webmercator'])
        set_geometry(gdf, 'the_geom', inplace=True)

        dataframe_columns_info = get_dataframe_columns_info(gdf)

        assert dataframe_columns_info == [
            ColumnInfo('cartodb_id', 'cartodb_id', 'bigint', False),
            ColumnInfo('the_geom', 'the_geom', 'geometry(Point, 4326)', True)
        ]

    def test_column_info_geometry_troubled_names(self):
        gdf = GeoDataFrame(
            [['POINT (0 0)', 'POINT (1 1)', 'POINT (2 2)']],
            columns=['Geom', 'the_geom', 'g-e-o-m-e-t-r-y'])
        set_geometry(gdf, 'the_geom', inplace=True)

        dataframe_columns_info = get_dataframe_columns_info(gdf)

        assert dataframe_columns_info == [
            ColumnInfo('Geom', 'geom', 'text', False),
            ColumnInfo('the_geom', 'the_geom', 'geometry(Point, 4326)', True),
            ColumnInfo('g-e-o-m-e-t-r-y', 'g_e_o_m_e_t_r_y', 'text', False)
        ]
