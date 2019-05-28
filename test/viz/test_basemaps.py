import unittest
from cartoframes.viz import basemaps


class TestBasemaps(unittest.TestCase):
    def test_is_defined(self):
        "basemaps"
        self.assertNotEqual(basemaps, None)

    def test_has_defined_basemaps(self):
        "basemaps content"
        self.assertEqual(basemaps.positron, 'Positron')
        self.assertEqual(basemaps.darkmatter, 'DarkMatter')
        self.assertEqual(basemaps.voyager, 'Voyager')
