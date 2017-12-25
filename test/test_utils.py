"""Unit tests for cartoframes.utils"""
import unittest
from cartoframes.utils import (dict_items, cssify, norm_colname,
                               normalize_colnames, importify_params)
from collections import OrderedDict


class TestUtils(unittest.TestCase):
    """Tests for functions in utils module"""
    def setUp(self):
        self.point_style = {
            "#layer['mapnik::geometry_type'=1]": OrderedDict([
                                              ('marker-width', "6"),
                                              ('marker-fill', "yellow"),
                                              ('marker-fill-opacity', "1"),
                                              ('marker-allow-overlap', "true"),
                                              ('marker-line-width', "0.5"),
                                              ('marker-line-color', "black"),
                                              ("marker-line-opacity", "1")])
            }

        self.polygon_style = {
                "#layer['mapnik::geometry_type'=3]": OrderedDict([
                    ('polygon-fill', ('ramp([column], (#ffc6c4, #ee919b, '
                                      '#cc607d, #9e3963, #672044), '
                                      'quantiles)')),
                    ('polygon-opacity', '0.9'),
                    ('polygon-gamma', '0.5'),
                    ('line-color', '#FFF'),
                    ('line-width', '0.5'),
                    ('line-opacity', '0.25'),
                    ('line-comp-op', 'hard-light')])}

        self.complex_style = OrderedDict([
            ("#layer['mapnik::geometry_type'=1]", OrderedDict([
                                              ('marker-width', "5"),
                                              ('marker-fill', "yellow"),
                                              ('marker-fill-opacity', '1'),
                                              ('marker-allow-overlap', 'true'),
                                              ('marker-line-width', '0.5'),
                                              ('marker-line-color', "black"),
                                              ('marker-line-opacity', '1')])),
            ("#layer['mapnik::geometry_type'=2]", OrderedDict([
                ('line-width', '1.5'),
                ('line-color', "black")])),
            ("#layer['mapnik::geometry_type'=3]", OrderedDict([
                ('polygon-fill', "blue"),
                ('polygon-opacity', '0.9'),
                ('polygon-gamma', '0.5'),
                ('line-color', '#FFF'),
                ('line-width', '0.5'),
                ('line-opacity', '0.25'),
                ('line-comp-op', 'hard-light')]))
        ])

        self.cols = ['Unnamed: 0', '201moore', 'Acadia 1.2.3',
                     'old_soaker', '_testingTesting', 1, 1.0]
        self.cols_ans = ['unnamed_0', '_201moore', 'acadia_1_2_3',
                         'old_soaker', '_testingtesting', '_1', '_1_0']

    def test_dict_items(self):
        """utils.dict_items"""
        # ensure correct formation of dict items from provided styling
        polygon_style_dict = dict_items(self.polygon_style)
        self.assertDictEqual(OrderedDict(polygon_style_dict),
                             self.polygon_style,
                             msg="pollygon styling")
        # point style
        point_style_dict = dict_items(self.point_style)
        self.assertDictEqual(OrderedDict(point_style_dict),
                             self.point_style,
                             msg="point styling")
        # multi layer styling
        complex_style_dict = dict_items(self.complex_style)
        self.assertDictEqual(OrderedDict(complex_style_dict),
                             self.complex_style,
                             msg="multi-layer styling")

    def test_cssify(self):
        """utils.cssify"""
        # point style
        point_stylecss = cssify(self.point_style)
        self.assertEqual(point_stylecss,
                         ("#layer['mapnik::geometry_type'=1] {  "
                          "marker-width: 6; marker-fill: yellow; "
                          "marker-fill-opacity: 1; marker-allow-overlap: "
                          "true; marker-line-width: 0.5; marker-line-color: "
                          "black; marker-line-opacity: 1;}"),
                         msg="point style")

        # polygon style
        polygon_stylecss = cssify(self.polygon_style)
        self.assertEqual(polygon_stylecss,
                         ("#layer['mapnik::geometry_type'=3] {  "
                          "polygon-fill: ramp([column], (#ffc6c4, #ee919b, "
                          "#cc607d, #9e3963, #672044), quantiles); "
                          "polygon-opacity: 0.9; polygon-gamma: 0.5; "
                          "line-color: #FFF; line-width: 0.5; line-opacity: "
                          "0.25; line-comp-op: hard-light;}"),
                         msg="polygon style")

        # complex style
        complex_stylecss = cssify(self.complex_style)
        self.assertEqual(complex_stylecss,
                         ("#layer['mapnik::geometry_type'=1] {  "
                          "marker-width: 5; marker-fill: yellow; "
                          "marker-fill-opacity: 1; marker-allow-overlap: "
                          "true; marker-line-width: 0.5; marker-line-color: "
                          "black; marker-line-opacity: 1;} "
                          "#layer['mapnik::geometry_type'=2] {  "
                          "line-width: 1.5; line-color: black;} "
                          "#layer['mapnik::geometry_type'=3] {  "
                          "polygon-fill: blue; polygon-opacity: 0.9; "
                          "polygon-gamma: 0.5; line-color: #FFF; line-width: "
                          "0.5; line-opacity: 0.25; "
                          "line-comp-op: hard-light;}"),
                         msg="multi-layer styling")

    def test_norm_colname(self):
        """utils.norm_colname"""
        for c, a in zip(self.cols, self.cols_ans):
            # changed cols should match answers
            self.assertEqual(norm_colname(c), a)
            # already sql-normed cols should match themselves
            self.assertEqual(norm_colname(a), a)

    def test_normalize_colnames(self):
        """utils.normalize_colnames"""
        self.assertListEqual(normalize_colnames(self.cols),
                             self.cols_ans,
                             msg='unnormalized should be SQL-normalized')
        self.assertListEqual(normalize_colnames(self.cols_ans),
                             self.cols_ans,
                             msg='already normalize columns should not change')

    def test_importify_params(self):
        """utils.importify_params"""
        params = [True, False, 'true', 'Gulab Jamon', ]
        ans = ('true', 'false', 'true', 'gulab jamon', )
        for idx, p in enumerate(params):
            self.assertTrue(importify_params(p), ans[idx])
