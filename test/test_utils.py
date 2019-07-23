# coding=UTF-8

"""Unit tests for cartoframes.utils"""
import unittest
import requests
from collections import OrderedDict

from cartoframes.utils import dict_items, cssify, importify_params, snake_to_camel, \
    camel_dictionary, debug_print


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

    def test_importify_params(self):
        """utils.importify_params"""
        params = [True, False, 'true', 'Gulab Jamon', ]
        ans = ('true', 'false', 'true', 'gulab jamon', )
        for idx, p in enumerate(params):
            self.assertTrue(importify_params(p), ans[idx])

    def test_dtypes2pg(self):
        """utils.dtypes2pg"""
        from cartoframes.utils import dtypes2pg
        results = {
            'float64': 'numeric',
            'int64': 'numeric',
            'float32': 'numeric',
            'int32': 'numeric',
            'object': 'text',
            'bool': 'boolean',
            'datetime64[ns]': 'timestamp',
            'unknown_dtype': 'text'
        }
        for i in results:
            self.assertEqual(dtypes2pg(i), results[i])

    def test_snake_to_camel(self):
        self.assertEqual(snake_to_camel('sneaky_snake'), 'sneakySnake')
        self.assertEqual(snake_to_camel('coolCamel'), 'coolCamel')
        self.assertEqual(snake_to_camel('kinky-kebab'), 'kinky-kebab')

    def test_camel_dictionary(self):
        test_dictionary = {'sneaky_snake': 'fang', 'coolCamel': 'hunch', 'kinky-kebab': 'spice'}

        camel_dictionary(test_dictionary)

        self.assertEqual(test_dictionary['sneakySnake'], 'fang')
        self.assertEqual(test_dictionary['coolCamel'], 'hunch')
        self.assertEqual(test_dictionary['kinky-kebab'], 'spice')
        with self.assertRaises(KeyError):
            self.assertEqual(test_dictionary['sneaky-snake'], None)

    def test_debug_print(self):
        # verbose = True
        verbose = 1

        # request-response usage
        resp = requests.get('http://httpbin.org/get')
        debug_print(verbose, resp=resp)
        debug_print(verbose, resp=resp.text)

        # non-requests-response usage
        test_str = 'this is a test'
        long_test_str = ', '.join([test_str] * 100)
        self.assertIsNone(debug_print(verbose, test_str=test_str))
        self.assertIsNone(debug_print(verbose, long_str=long_test_str))

        # verbose = False
        verbose = 0
        self.assertIsNone(debug_print(verbose, resp=test_str))
