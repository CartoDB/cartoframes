"""Unit tests for cartoframes.utils"""
import unittest
from cartoframes.utils import dict_items, cssify
from cartoframes import styling
from collections import OrderedDict
# from cartoframes import styling

class TestUtils(unittest.TestCase):
    """Tests for functions in utils module"""
    def setUp(self):
        self.point_style = OrderedDict([(
                            "#layer['mapnik::geometry_type'=1]", OrderedDict([
                                ('marker-width', "6"),
                                ('marker-fill', "yellow"),
                                ('marker-fill-opacity', "1"),
                                ('marker-allow-overlap', "true"),
                                ('marker-line-width', "0.5"),
                                ('marker-line-color', "black"),
                                ("marker-line-opacity", "1")])
                            )])
        self.point_style_dict = dict_items(self.point_style)
        self.point_stylecss = cssify(self.point_style)
        self.polygon_style = OrderedDict([(
                                "#layer['mapnik::geometry_type'=3]", OrderedDict([
                                    ('polygon-fill', 'ramp([column], (#ffc6c4, #ee919b, #cc607d, #9e3963, #672044), quantiles)'),
                                    ('polygon-opacity', '0.9'),
                                    ('polygon-gamma', '0.5'),
                                    ('line-color', '#FFF'),
                                    ('line-width', '0.5'),
                                    ('line-opacity', '0.25'),
                                    ('line-comp-op', 'hard-light')])
                                )])
        self.polygon_style_dict = dict_items(self.polygon_style)
        self.polygon_stylecss = cssify(self.polygon_style)

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

        self.complex_style_dict = dict_items(self.complex_style)
        self.complex_stylecss = cssify(self.complex_style)

    def test_dict_items(self):
        """utils.dict_items"""
        # ensure correct formation of dict items from provided styling
        self.assertEqual(OrderedDict(self.polygon_style_dict),
                         self.polygon_style)
        self.assertEqual(OrderedDict(self.point_style_dict),
                         self.point_style)
        self.assertEqual(OrderedDict(self.complex_style_dict),
                         self.complex_style)

    def test_cssify(self):
        """utils.cssify"""
        self.assertEqual(self.point_stylecss,
                         "#layer['mapnik::geometry_type'=1] {  marker-width: 6; marker-fill: yellow; marker-fill-opacity: 1; marker-allow-overlap: true; marker-line-width: 0.5; marker-line-color: black; marker-line-opacity: 1;} ")
        self.assertEqual(self.polygon_stylecss,
                         "#layer['mapnik::geometry_type'=3] {  polygon-fill: ramp([column], (#ffc6c4, #ee919b, #cc607d, #9e3963, #672044), quantiles); polygon-opacity: 0.9; polygon-gamma: 0.5; line-color: #FFF; line-width: 0.5; line-opacity: 0.25; line-comp-op: hard-light;} ")
        self.assertEqual(self.complex_stylecss,
                         "#layer['mapnik::geometry_type'=1] {  marker-width: 5; marker-fill: yellow; marker-fill-opacity: 1; marker-allow-overlap: true; marker-line-width: 0.5; marker-line-color: black; marker-line-opacity: 1;} #layer['mapnik::geometry_type'=2] {  line-width: 1.5; line-color: black;} #layer['mapnik::geometry_type'=3] {  polygon-fill: blue; polygon-opacity: 0.9; polygon-gamma: 0.5; line-color: #FFF; line-width: 0.5; line-opacity: 0.25; line-comp-op: hard-light;} ")
