"""Unit tests for cartoframes.layers"""
import json
import unittest
from cartoframes.layer import BaseMap, Layer, QueryLayer
from cartoframes.maps import (non_basemap_layers, has_time_layer, get_map_name,
                              get_map_template)


class TestMaps(unittest.TestCase):
    """Tests for functions in maps module"""
    def setUp(self):
        self.layers = [BaseMap('dark'),
                       Layer('cb_2013_puma10_500k',
                             color='grey'),
                       Layer('tweets_obama',
                             color='yellow',
                             size='favoritescount')]

        self.layers_w_time = [BaseMap('dark', labels='front'),
                              Layer('acadia'),
                              QueryLayer('select * from acadia limit 10',
                                         time='foo'),
                              Layer('biodiversity'),
                              BaseMap('dark',
                                      labels='front',
                                      only_labels=True)]

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

        # If nothing is passed
        nbm_nothing = non_basemap_layers([])
        self.assertEqual(len(nbm_nothing), 0)

    def test_has_time_layer(self):
        """maps.has_time_layers"""
        layers_no_time = has_time_layer(self.layers)
        layers_w_time = has_time_layer(self.layers_w_time)
        self.assertFalse(layers_no_time)
        self.assertTrue(layers_w_time)

    def test_get_map_name(self):
        """maps.get_map_name"""
        map_name = get_map_name(self.layers,
                                has_zoom=False)
        self.assertEqual(
            map_name,
            'cartoframes_ver20170406_layers2_time0_baseid1_labels0_zoom0')
        self.assertEqual(
            get_map_name(self.layers, has_zoom=True),
            'cartoframes_ver20170406_layers2_time0_baseid1_labels0_zoom1')
        self.assertEqual(
            get_map_name(self.layers_w_time, has_zoom=False),
            'cartoframes_ver20170406_layers3_time1_baseid1_labels1_zoom0')

    def test_map_template(self):
        """maps.map_template_dict"""
        map_template = get_map_template(self.layers, has_zoom=False)
        filledtemplate = {
            "placeholders": {
                "north": {
                    "default": 45,
                    "type": "number"
                },
                "cartocss_1": {
                    "default": ("#layer { "
                                "marker-fill: red; "
                                "marker-width: 5; "
                                "marker-allow-overlap: true; "
                                "marker-line-color: #000; "
                                "}"),
                    "type": "sql_ident"
                },
                "cartocss_0": {
                    "default": ("#layer { "
                                "marker-fill: red; "
                                "marker-width: 5; "
                                "marker-allow-overlap: true; "
                                "marker-line-color: #000; }"),
                    "type": "sql_ident"
                },
                "west": {
                    "default": -45,
                    "type": "number"
                },
                "east": {
                    "default": 45,
                    "type": "number"
                },
                "sql_0": {
                    "default": ("SELECT ST_PointFromText('POINT(0 0)', "
                                "4326) AS the_geom, 1 AS cartodb_id, "
                                "ST_PointFromText('Point(0 0)', 3857) AS "
                                "the_geom_webmercator"),
                    "type": "sql_ident"
                },
                "sql_1": {
                    "default": ("SELECT ST_PointFromText('POINT(0 0)', "
                                "4326) AS the_geom, 1 AS cartodb_id, "
                                "ST_PointFromText('Point(0 0)', 3857) AS "
                                "the_geom_webmercator"),
                    "type": "sql_ident"
                },
                "south": {
                    "default": -45,
                    "type": "number"
                    }
                },
            "version": "0.0.1",
            "name": ("cartoframes_ver20170406_layers2_time0_baseid1_"
                     "labels0_zoom0"),
            "layergroup": {
                "layers": [
                    {
                        "type": "http",
                        "options": {
                            "urlTemplate": ("https://{s}.basemaps."
                                            "cartocdn.com/rastertiles"
                                            "/dark_all/{z}/{x}/{y}."
                                            "png"),
                            "subdomains": "abcd"
                        }
                    },
                    {
                        "type": "mapnik",
                        "options": {
                            "cartocss": "<%= cartocss_0 %>",
                            "sql": "<%= sql_0 %>",
                            "cartocss_version": "2.1.1"
                        }
                    },
                    {
                        "type": "mapnik",
                        "options": {
                            "cartocss": "<%= cartocss_1 %>",
                            "sql": "<%= sql_1 %>",
                            "cartocss_version": "2.1.1"
                        }
                    }],
                "version": "1.0.1"
            },
            "view": {
                "bounds": {
                    "west": "<%= west %>",
                    "east": "<%= east %>",
                    "north": "<%= north %>",
                    "south": "<%= south %>"
                }
            }
        }

        map_template_dict = json.loads(map_template)
        self.assertDictEqual(map_template_dict, filledtemplate)
