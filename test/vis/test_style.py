import unittest
from cartoframes import vis


class TestStyle(unittest.TestCase):
    def test_is_style_defined(self):
        """vis.Style"""
        self.assertNotEqual(vis.Style, None)

    def test_is_style_defined(self):
        """vis.Style should initialize style defaults without params"""
        style = vis.Style()

        expected = '''color: hex("#EE4D5A")
width: ramp(linear(zoom(),0,18),[2,10])
strokeWidth: ramp(linear(zoom(),0,18),[0,1])
strokeColor: opacity(#222,ramp(linear(zoom(),0,18),[0,1]))
'''
        self.assertEqual(style.compute_viz('point'), expected)

    def test_style_string(self):
        """vis.Style should initialize style from a string with defaults"""
        style = vis.Style('color: red')

        defaults = 'width: ramp(linear(zoom(),0,18),[0.5,4])\n'
        expected = defaults + 'color: red'
        self.assertEqual(style.compute_viz('line'), expected)

    def test_style_dictionary(self):
        """vis.Style should initialize style from a dict with defaults"""
        style = vis.Style({'color': 'red', 'strokeWidth': 0 })

        defaults = 'strokeColor: opacity(#2c2c2c,ramp(linear(zoom(),2,18),[0.2,0.6]))\n'
        expected = 'color: red\nstrokeWidth: 0\n' + defaults
        self.assertEqual(style.compute_viz('polygon'), expected)

    def test_wrong_attribute(self):
        """vis.Style should raise an error if style property is not valid"""
        with self.assertRaises(ValueError):
            vis.Style({'wrong': 'red'}).compute_viz('point')
