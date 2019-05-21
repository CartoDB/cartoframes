import unittest
from cartoframes import vis

DEFAULT_STYLE_POINT = '''color: hex("#EE4D5A")
width: ramp(linear(zoom(),0,18),[2,10])
strokeWidth: ramp(linear(zoom(),0,18),[0,1])
strokeColor: opacity(#222,ramp(linear(zoom(),0,18),[0,1]))
'''

class TestStyle(unittest.TestCase):
    def test_is_style_defined(self):
        """vis.Style"""
        self.assertNotEqual(vis.Style, None)

    def test_style_default(self):
        """vis.Style.compute_viz should return the default viz without params"""
        style = vis.Style()

        self.assertEqual(style.compute_viz('point'), DEFAULT_STYLE_POINT)

    def test_style_string(self):
        """vis.Style.compute_viz should return the viz from a string with defaults"""
        style = vis.Style('@var: 1\ncolor: red')

        defaults = 'width: ramp(linear(zoom(),0,18),[0.5,4])\n'
        expected = defaults + '@var: 1\ncolor: red'
        self.assertEqual(style.compute_viz('line'), expected)

    def test_style_dict(self):
        """vis.Style.compute_viz should return the viz from a dict with defaults"""
        style = vis.Style({
            'vars': {
                'var': 1
            },
            'color': 'red',
            'strokeWidth': 0
        })
    
        defaults = 'strokeColor: opacity(#2c2c2c,ramp(linear(zoom(),2,18),[0.2,0.6]))\n'
        expected = '@var: 1\ncolor: red\nstrokeWidth: 0\n' + defaults
        self.assertEqual(style.compute_viz('polygon'), expected)

    def test_style_default_variables(self):
        """vis.Style.compute_viz should return the default viz with the variables"""
        style = vis.Style()

        variables = '@mimi: "123"\n@momo: 123\n'
        expected = variables + DEFAULT_STYLE_POINT
        self.assertEqual(style.compute_viz('point', {
            'mimi': '123',
            'momo': 123
        }), expected)

    def test_style_string_variables(self):
        """vis.Style.compute_viz should return the string viz with the variables"""
        style = vis.Style('@var: 1\ncolor: red')

        variables = '@mimi: "123"\n@momo: 123\n'
        defaults = 'width: ramp(linear(zoom(),0,18),[0.5,4])\n'
        expected = variables + defaults + '@var: 1\ncolor: red'
        self.assertEqual(style.compute_viz('line', {
            'mimi': '123',
            'momo': 123
        }), expected)

    def test_style_dict_variables(self):
        """vis.Style.compute_viz should return the dict viz with the variables"""
        style = vis.Style({
            'vars': {
                'var': 1
            },
            'color': 'red',
            'strokeWidth': 0
        })

        variables = '@mimi: "123"\n@momo: 123\n'
        defaults = 'strokeColor: opacity(#2c2c2c,ramp(linear(zoom(),2,18),[0.2,0.6]))\n'
        expected = '@var: 1\n' + variables + 'color: red\nstrokeWidth: 0\n' + defaults
        self.assertEqual(style.compute_viz('polygon', {
            'mimi': '123',
            'momo': 123
        }), expected)

    def test_wrong_attribute(self):
        """vis.Style should raise an error if style property is not valid"""
        with self.assertRaises(ValueError):
            vis.Style({'wrong': 'red'}).compute_viz('point')
