import unittest
from cartoframes import carto_vl


class TestStyles(unittest.TestCase):
    def test_is_style_defined(self):
        self.assertNotEqual(carto_vl.Style, None)

    def test_initialization(self):
        """should initialize style attributes"""
        style = carto_vl.Style('color: red')

        self.assertEqual(style.viz, 'color: red')
