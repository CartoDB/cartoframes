# coding=UTF-8

"""Unit tests for cartoframes.data.columns"""

from cartoframes import CartoDataFrame
from cartoframes.utils.columns import (Column, DataframeColumnInfo,
                                       DataframeColumnsInfo, normalize_names)


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

    def test_database_column_name_the_geom(self):
        dataframe_column_info = DataframeColumnInfo('other')
        assert dataframe_column_info.name == 'other'
        dataframe_column_info = DataframeColumnInfo('the_geom', 'geometry')
        assert dataframe_column_info.name == 'the_geom'
        assert dataframe_column_info.type == 'geometry(Point, 4326)'

    def test_column_info_with_geom(self):
        cdf = CartoDataFrame(
            [['Gran Vía 46', 'Madrid', 'POINT (0 0)'], ['Ebro 1', 'Sevilla', 'POINT (1 1)']],
            columns=['address', 'city', 'the_geom'],
            geometry='the_geom'
        )

        expected_columns = [
            {'name': 'address', 'type': 'text'},
            {'name': 'city', 'type': 'text'},
            {'name': 'the_geom', 'type': 'geometry(Point, 4326)'}
        ]

        dataframe_columns_info = DataframeColumnsInfo(cdf)

        assert len(dataframe_columns_info.columns) == 3
        assert dataframe_columns_info.columns[0].name == expected_columns[0]['name']
        assert dataframe_columns_info.columns[0].type == expected_columns[0]['type']
        assert dataframe_columns_info.columns[1].name == expected_columns[1]['name']
        assert dataframe_columns_info.columns[1].type == expected_columns[1]['type']
        assert dataframe_columns_info.columns[2].name == expected_columns[2]['name']
        assert dataframe_columns_info.columns[2].type == expected_columns[2]['type']

    def test_column_info_without_geom(self):
        cdf = CartoDataFrame(
            [['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']],
            columns=['address', 'city']
        )

        expected_columns = [
            {'name': 'address', 'type': 'text'},
            {'name': 'city', 'type': 'text'}
        ]

        dataframe_columns_info = DataframeColumnsInfo(cdf)

        assert len(dataframe_columns_info.columns) == 2
        assert dataframe_columns_info.columns[0].name == expected_columns[0]['name']
        assert dataframe_columns_info.columns[0].type == expected_columns[0]['type']
        assert dataframe_columns_info.columns[1].name == expected_columns[1]['name']
        assert dataframe_columns_info.columns[1].type == expected_columns[1]['type']

    def test_column_info_basic_troubled_names(self):
        cdf = CartoDataFrame(
            [[1, 'POINT (1 1)', 'fake_geom']],
            columns=['cartodb_id', 'the_geom', 'the_geom_webmercator'],
            geometry='the_geom'
        )

        expected_columns = [
            {'name': 'cartodb_id', 'type': 'bigint'},
            {'name': 'the_geom', 'type': 'geometry(Point, 4326)'}
        ]

        dataframe_columns_info = DataframeColumnsInfo(cdf)

        assert len(dataframe_columns_info.columns) == 2
        assert dataframe_columns_info.columns[0].name == expected_columns[0]['name']
        assert dataframe_columns_info.columns[0].type == expected_columns[0]['type']
        assert dataframe_columns_info.columns[1].name == expected_columns[1]['name']
        assert dataframe_columns_info.columns[1].type == expected_columns[1]['type']

    def test_column_info_geometry_troubled_names(self):
        cdf = CartoDataFrame(
            [['POINT (0 0)', 'POINT (1 1)', 'POINT (2 2)']],
            columns=['geom', 'the_geom', 'geometry'],
            geometry='the_geom'
        )

        expected_columns = [
            {'name': 'geom', 'type': 'text'},
            {'name': 'the_geom', 'type': 'geometry(Point, 4326)'},
            {'name': 'geometry', 'type': 'text'}
        ]

        dataframe_columns_info = DataframeColumnsInfo(cdf)

        assert len(dataframe_columns_info.columns) == 3
        assert dataframe_columns_info.columns[0].name == expected_columns[0]['name']
        assert dataframe_columns_info.columns[0].type == expected_columns[0]['type']
        assert dataframe_columns_info.columns[1].name == expected_columns[1]['name']
        assert dataframe_columns_info.columns[1].type == expected_columns[1]['type']
        assert dataframe_columns_info.columns[2].name == expected_columns[2]['name']
        assert dataframe_columns_info.columns[2].type == expected_columns[2]['type']
