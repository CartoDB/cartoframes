import unittest
from cartoframes import carto_vl


class TestBasemaps(unittest.TestCase):
    def test_is_defined(self):
        self.assertNotEqual(carto_vl.basemaps, None)

    def test_has_defined_basemaps(self):
        self.assertEqual(carto_vl.basemaps.positron, 'Positron')
        self.assertEqual(carto_vl.basemaps.darkmatter, 'DarkMatter')
        self.assertEqual(carto_vl.basemaps.voyager, 'Voyager')
