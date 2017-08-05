"""Unit tests for cartoframes.layers"""
import unittest
from cartoframes.layer import BaseMap, Layer, QueryLayer
from cartoframes.maps import (non_basemap_layers, has_time_layer, get_map_name, 
                              get_map_template)
import ast


class TestMaps(unittest.TestCase):
    """Tests for functions in maps module"""
    def setUp(self):
        self.layers = [BaseMap('dark'),
                       Layer('cb_2013_puma10_500k',
                             color='grey'),
                       Layer('tweets_obama',
                             color='yellow',
                             size='favoritescount')]

        self.layer_with_time = has_time_layer(self.layers)
        self.map_template = get_map_template(self.layers, has_zoom=False)
        # TODO: change this to a dict
        self.js = '{"placeholders": {"north": {"default": 45, "type": "number"}, "cartocss_1": {"default": "#layer { marker-fill: red; marker-width: 5; marker-allow-overlap: true; marker-line-color: #000; }", "type": "sql_ident"}, "cartocss_0": {"default": "#layer { marker-fill: red; marker-width: 5; marker-allow-overlap: true; marker-line-color: #000; }", "type": "sql_ident"}, "west": {"default": -45, "type": "number"}, "east": {"default": 45, "type": "number"}, "sql_0": {"default": "SELECT ST_PointFromText(\'POINT(0 0)\', 4326) as the_geom, 1 as cartodb_id, ST_PointFromText(\'Point(0 0)\', 3857) as the_geom_webmercator", "type": "sql_ident"}, "sql_1": {"default": "SELECT ST_PointFromText(\'POINT(0 0)\', 4326) as the_geom, 1 as cartodb_id, ST_PointFromText(\'Point(0 0)\', 3857) as the_geom_webmercator", "type": "sql_ident"}, "south": {"default": -45, "type": "number"}}, "version": "0.0.1", "name": "cartoframes_ver20170406_layers2_time0_baseid1_labels0_zoom0", "layergroup": {"layers": [{"type": "http", "options": {"urlTemplate": "https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png", "subdomains": "abcd"}}, {"type": "mapnik", "options": {"cartocss": "<%= cartocss_0 %>", "sql": "<%= sql_0 %>", "cartocss_version": "2.1.1"}}, {"type": "mapnik", "options": {"cartocss": "<%= cartocss_1 %>", "sql": "<%= sql_1 %>", "cartocss_version": "2.1.1"}}], "version": "1.0.1"}, "view": {"bounds": {"west": "<%= west %>", "east": "<%= east %>", "north": "<%= north %>", "south": "<%= south %>"}}}'

        self.js_dict = ast.literal_eval(self.js)
        self.map_template_dict = ast.literal_eval(self.map_template)

    def test_non_basemap_layers(self):
        """maps.non_basemap_layers"""
        nbm_layers = non_basemap_layers(self.layers)
        # ensure the layers are separated out correctly
        self.assertEqual(self.layers[1],
                         nbm_layers[0],
                         msg=('first non-basemap layer should be second layer '
                              'in original layer list'))

        self.assertEqual(self.layers[2],
                         nbm_layers[1],
                         msg=('second non-basemap layer should be third layer '
                              'in original layer list'))

        # correct number of layers passed out
        self.assertEqual(len(nbm_layers), 2)

        # If no data layers exist, non_basemap_layers should be an empty list
        nbm_no_layers = non_basemap_layers([BaseMap()])
        self.assertEqual(len(nbm_no_layers), 0)

    def test_has_time_layer(self):
        """maps.has_time_layers"""
        self.assertEqual(self.layer_with_time, False)

    def test_get_map_name(self):
        """maps.get_map_name"""
        map_name = get_map_name(self.layers,
                                has_zoom=False)
        self.assertEqual(map_name,
                         'cartoframes_ver20170406_layers2_time0_baseid1_labels0_zoom0')
        self.assertEqual(get_map_name(self.layers, has_zoom=True),
                         'cartoframes_ver20170406_layers2_time0_baseid1_labels0_zoom1')
        layers_w_time = [BaseMap('dark', labels='front'),
                         Layer('acadia'),
                         QueryLayer('select * from acadia limit 10',
                                    time='foo'),
                         Layer('biodiversity'),
                         BaseMap('dark', labels='front', only_labels=True)]
        self.assertEqual(get_map_name(layers_w_time, has_zoom=False),
                         'cartoframes_ver20170406_layers3_time1_baseid1_labels1_zoom0')

    def test_map_template(self):
        """maps.map_template_dict"""
        # TODO: This could be handled but just doing a direct comparison of the
        #       two dicts:
        self.assertEqual(self.map_template_dict,
                         self.js_dict)
        self.assertEqual(self.map_template_dict['version'],
                         self.js_dict['version'])
        self.assertEqual(self.map_template_dict['name'],
                         self.js_dict['name'])
        self.assertEqual(self.map_template_dict['placeholders'],
                         self.js_dict['placeholders'])
        self.assertEqual(self.map_template_dict['layergroup'],
                         self.js_dict['layergroup'])
        self.assertEqual(self.map_template_dict['view'],
                         self.js_dict['view'])
