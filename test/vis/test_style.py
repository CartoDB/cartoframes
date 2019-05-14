import unittest
from cartoframes import vis


class TestStyle(unittest.TestCase):
    def test_is_style_defined(self):
        self.assertNotEqual(vis.Style, None)

    def test_style_string(self):
        """should initialize style attributes from a string"""
        style = vis.Style('color: red')

        self.assertEqual(style.viz, 'color: red')

    def test_style_dictionary(self):
        """should initialize style attributes from a dict"""
        style = vis.Style({'color': 'red'})

        self.assertEqual(style.viz, 'color: red')

    def test_wrong_attribute(self):
        """should raise an error if style property is not valid"""

        with self.assertRaises(ValueError):
            vis.Style({'wrong': 'red'})
