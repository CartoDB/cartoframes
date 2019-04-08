import unittest
from cartoframes.carto_vl import carto


class TestBasemaps(unittest.TestCase):
    def test_is_defined(self):
        self.assertNotEqual(carto.Basemaps, None)

    def test_has_defined_basemaps(self):
        self.assertEqual(carto.Basemaps.positron, 'positron')
        self.assertEqual(carto.Basemaps.darkmatter, 'darkmatter')
        self.assertEqual(carto.Basemaps.voyager, 'voyager')
