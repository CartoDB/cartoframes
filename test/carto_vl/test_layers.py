import unittest
from cartoframes import carto_vl


class TestLayers(unittest.TestCase):
    def test_is_layer_defined(self):
        self.assertNotEqual(carto_vl.Layer, None)

    def test_is_local_layer_defined(self):
        self.assertNotEqual(carto_vl.LocalLayer, None)

    def test_is_query_layer_defined(self):
        self.assertNotEqual(carto_vl.QueryLayer, None)
