import unittest
from cartoframes import carto_vl


class TestCartoVL(unittest.TestCase):
    def test_is_defined(self):
        self.assertNotEqual(carto_vl, None)
