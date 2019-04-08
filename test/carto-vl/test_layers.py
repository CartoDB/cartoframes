import unittest
from cartoframes.carto_vl import carto


class TestLayers(unittest.TestCase):
    def test_is_layer_defined(self):
        self.assertNotEqual(carto.Layer, None)

    def test_is_local_layer_defined(self):
        self.assertNotEqual(carto.LocalLayer, None)

    def test_is_query_layer_defined(self):
        self.assertNotEqual(carto.QueryLayer, None)
