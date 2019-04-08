import unittest
from cartoframes.carto_vl import carto


class TestMap(unittest.TestCase):
    def test_is_defined(self):
        self.assertNotEqual(carto.Map, None)
