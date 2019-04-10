# coding=UTF-8

"""Unit tests for cartoframes.columns"""
import unittest

from cartoframes.columns import Column, normalize_names


class TestColumns(unittest.TestCase):
    """Tests for functions in columns module"""
    def setUp(self):
        self.cols = ['Unnamed: 0',
                     '201moore',
                     '201moore',
                     'Acadia 1.2.3',
                     'old_soaker',
                     '_testingTesting',
                     1,
                     1.0,
                     'public',
                     'SELECT',
                     'à',
                     'aa',
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
                         '_1',
                         '_1_0',
                         'public',
                         '_select',
                         'aa',
                         'aa_1',
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
