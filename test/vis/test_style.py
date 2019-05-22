import unittest
from cartoframes import vis


class TestStyle(unittest.TestCase):
    def test_is_style_defined(self):
        """vis.Style"""
        self.assertNotEqual(vis.Style, None)

    def test_style_string(self):
        """vis.Style should initialize style attributes from a string"""
        style = vis.Style('color: red')

        self.assertEqual(style.compute_viz(), 'color: red')

    def test_style_dictionary(self):
        """vis.Style should initialize style attributes from a dict"""
        style = vis.Style({'color': 'red'})

        self.assertEqual(style.compute_viz(), 'color: red\n')

    def test_wrong_attribute(self):
        """vis.Style should raise an error if style property is not valid"""
        with self.assertRaises(ValueError):
            vis.Style({'wrong': 'red'}).compute_viz()
