"""Unit tests for cartoframes.layers"""
import unittest
from cartoframes.layer import BaseMap, Layer, QueryLayer
from cartoframes.maps import non_basemap_layers, has_time_layer, get_map_name, get_map_template
from cartoframes.layer import BaseMap


class TestMaps(unittest.TestCase):
    """ Tests for functions in maps module"""
    def setUp(self):
        self.layers = [BaseMap('dark'),
                       Layer('cb_2013_puma10_500k',
                             color='grey'),
                       Layer('tweets_obama',
                             color='yellow',
                             size='favoritescount')
                       ]
        self.nbm_layers = non_basemap_layers(self.layers)
        self.layer_with_time = has_time_layer(self.layers)
        self.map_name = get_map_name(self.layers, has_zoom=False)

    def test_non_basemap_layers(self):
        self.assertEqual(self.layers[1],
                         self.nbm_layers[0])

        self.assertEqual(self.layers[2],
                         self.nbm_layers[1])

    def test_has_time_layer(self):
        self.assertEqual(self.layer_with_time, False)

    def test_get_map_name(self):
        self.assertEqual(self.map_name,
                         'cartoframes_ver20170406_layers2_time0_baseid1_labels0_zoom0')
