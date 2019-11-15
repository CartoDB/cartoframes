# coding=UTF-8

"""Unit tests for cartoframes.data.columns"""
import unittest

import pandas as pd

from cartoframes.utils.columns import (Column, DataframeColumnInfo,
                                       DataframeColumnsInfo, normalize_names)


class TestColumns(unittest.TestCase):
    """Tests for functions in columns module"""

    def setUp(self):
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
            self.assertEqual(column.name, a)
            # already sql-normed cols should match themselves
            self.assertEqual(a_column.name, a)
            other_cols.append(column.name)

    def test_normalize_names(self):
        self.assertListEqual(normalize_names(self.cols), self.cols_ans)

    def test_normalize_names_unchanged(self):
        self.assertListEqual(normalize_names(self.cols_ans), self.cols_ans)

    def test_database_column_name_the_geom(self):
        geom_column = 'the_geom'

        dataframe_column_info = DataframeColumnInfo('other', geom_column)
        self.assertEqual(dataframe_column_info.database, 'other')
        dataframe_column_info = DataframeColumnInfo('the_geom', geom_column)
        self.assertEqual(dataframe_column_info.database, 'the_geom')

        geom_column = 'other_geom'

        dataframe_column_info = DataframeColumnInfo('other', geom_column)
        self.assertEqual(dataframe_column_info.database, 'other')
        dataframe_column_info = DataframeColumnInfo('the_geom', geom_column)
        self.assertEqual(dataframe_column_info.database, 'the_geom')

    def test_column_info_with_geom(self):
        df = pd.DataFrame(
            [['Gran Vía 46', 'Madrid', 'POINT (0 0)'], ['Ebro 1', 'Sevilla', 'POINT (1 1)']],
            columns=['address', 'city', 'geometry'])

        expected_columns = [
            {
                'dataframe': 'address',
                'database': 'address',
                'database_type': 'text'
            },
            {
                'dataframe': 'city',
                'database': 'city',
                'database_type': 'text'
            },
            {
                'dataframe': 'geometry',
                'database': 'the_geom',
                'database_type': 'geometry(Point, 4326)'
            }
        ]
        expected_geom_column = 'geometry'
        expected_enc_type = 'wkt'

        dataframe_columns_info = DataframeColumnsInfo(df, None)

        self.assertEqual(expected_columns, dataframe_columns_info.columns)
        self.assertEqual(expected_geom_column, dataframe_columns_info.geom_column)
        self.assertEqual(expected_enc_type, dataframe_columns_info.enc_type)

    def test_column_info_with_lnglat(self):
        df = pd.DataFrame([['0', '1'], ['0', '1']], columns=['lng', 'lat'])

        expected_columns = [
            {
                'dataframe': 'lng',
                'database': 'lng',
                'database_type': 'text'
            },
            {
                'dataframe': 'lat',
                'database': 'lat',
                'database_type': 'text'
            },
            {
                'dataframe': None,
                'database': 'the_geom',
                'database_type': 'geometry(Point, 4326)'
            }
        ]
        expected_geom_column = None
        expected_enc_type = None

        dataframe_columns_info = DataframeColumnsInfo(df, ('lng', 'lat'))

        self.assertEqual(expected_columns, dataframe_columns_info.columns)
        self.assertEqual(expected_geom_column, dataframe_columns_info.geom_column)
        self.assertEqual(expected_enc_type, dataframe_columns_info.enc_type)

    def test_column_info_without_geom(self):
        df = pd.DataFrame(
            [['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address', 'city'])

        expected_columns = [
            {
                'dataframe': 'address',
                'database': 'address',
                'database_type': 'text'
            },
            {
                'dataframe': 'city',
                'database': 'city',
                'database_type': 'text'
            }
        ]
        expected_geom_column = None
        expected_enc_type = None

        dataframe_columns_info = DataframeColumnsInfo(df, None)

        self.assertEqual(expected_columns, dataframe_columns_info.columns)
        self.assertEqual(expected_geom_column, dataframe_columns_info.geom_column)
        self.assertEqual(expected_enc_type, dataframe_columns_info.enc_type)

    def test_column_info_basic_troubled_names(self):
        df = pd.DataFrame(
            [[1, 'POINT (1 1)', 'fake_geom']], columns=['cartodb_id', 'the_geom', 'the_geom_webmercator'])

        expected_columns = [
            {
                'dataframe': 'cartodb_id',
                'database': 'cartodb_id',
                'database_type': 'bigint'
            },
            {
                'dataframe': 'the_geom',
                'database': 'the_geom',
                'database_type': 'geometry(Point, 4326)'
            }
        ]
        expected_geom_column = 'the_geom'
        expected_enc_type = 'wkt'

        dataframe_columns_info = DataframeColumnsInfo(df, None)

        self.assertEqual(expected_columns, dataframe_columns_info.columns)
        self.assertEqual(expected_geom_column, dataframe_columns_info.geom_column)
        self.assertEqual(expected_enc_type, dataframe_columns_info.enc_type)

    def test_column_info_geometry_troubled_names(self):
        df = pd.DataFrame(
            [['POINT (0 0)', 'POINT (1 1)', 'POINT (2 2)']], columns=['geom', 'the_geom', 'geometry'])

        expected_columns = [
            {
                'dataframe': 'geom',
                'database': 'geom',
                'database_type': 'text'
            },
            {
                'dataframe': 'the_geom',
                'database': 'the_geom',
                'database_type': 'geometry(Point, 4326)'
            },
            {
                'dataframe': 'geometry',
                'database': 'geometry',
                'database_type': 'text'
            },
        ]
        expected_geom_column = 'the_geom'
        expected_enc_type = 'wkt'

        dataframe_columns_info = DataframeColumnsInfo(df, None)

        self.assertEqual(expected_columns, dataframe_columns_info.columns)
        self.assertEqual(expected_geom_column, dataframe_columns_info.geom_column)
        self.assertEqual(expected_enc_type, dataframe_columns_info.enc_type)
