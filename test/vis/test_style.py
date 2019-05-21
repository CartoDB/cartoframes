import unittest
from cartoframes import vis


class TestStyle(unittest.TestCase):
    def test_is_style_defined(self):
        """vis.Style"""
        self.assertNotEqual(vis.Style, None)

    def test_style_default_point(self):
        """vis.Style.compute_viz should return the default viz for point"""
        style = vis.Style()
        viz = style.compute_viz('point')

        self.assertIn('color: hex("#EE4D5A")', viz)
        self.assertIn('width: ramp(linear(zoom(),0,18),[2,10])', viz)
        self.assertIn('strokeWidth: ramp(linear(zoom(),0,18),[0,1])', viz)
        self.assertIn('strokeColor: opacity(#222,ramp(linear(zoom(),0,18),[0,1]))', viz)

    def test_style_default_line(self):
        """vis.Style.compute_viz should return the default viz for line"""
        style = vis.Style()
        viz = style.compute_viz('line')

        self.assertIn('color: hex("#4CC8A3")', viz)
        self.assertIn('width: ramp(linear(zoom(),0,18),[0.5,4])', viz)

    def test_style_default_polygon(self):
        """vis.Style.compute_viz should return the default viz for polygon"""
        style = vis.Style()
        viz = style.compute_viz('polygon')

        self.assertIn('color: hex("#826DBA")', viz)
        self.assertIn('strokeWidth: ramp(linear(zoom(),2,18),[0.5,1])', viz)
        self.assertIn('strokeColor: opacity(#2c2c2c,ramp(linear(zoom(),2,18),[0.2,0.6]))', viz)

    def test_style_string(self):
        """vis.Style.compute_viz should return the viz from a string with defaults"""
        style = vis.Style('@var: 1\ncolor: red')
        viz = style.compute_viz('line')
    
        self.assertIn('@var: 1', viz)
        self.assertIn('color: red', viz)
        self.assertIn('width: ramp(linear(zoom(),0,18),[0.5,4])', viz)
        self.assertNotIn('color: hex("#4CC8A3")', viz)

    def test_style_dict(self):
        """vis.Style.compute_viz should return the viz from a dict with defaults"""
        style = vis.Style({
            'vars': {
                'var': 1
            },
            'color': 'red',
            'strokeWidth': 0
        })
        viz = style.compute_viz('polygon')

        self.assertIn('@var: 1', viz)
        self.assertIn('color: red', viz)
        self.assertIn('strokeWidth: 0', viz)
        self.assertIn('strokeColor: opacity(#2c2c2c,ramp(linear(zoom(),2,18),[0.2,0.6]))', viz)
        self.assertNotIn('color: hex("#826DBA")', viz)
        self.assertNotIn('strokeWidth: ramp(linear(zoom(),2,18),[0.5,1])', viz)

    def test_style_default_variables(self):
        """vis.Style.compute_viz should return the default viz with the variables"""
        style = vis.Style()
        viz = style.compute_viz('point', {
            'mimi': '$pop',
            'momo': 123
        })

        self.assertIn('@mimi: $pop', viz)
        self.assertIn('@momo: 123', viz)

    def test_style_string_variables(self):
        """vis.Style.compute_viz should return the string viz with the variables"""
        style = vis.Style('@var: 1')
        viz = style.compute_viz('line', {
            'mimi': '$pop',
            'momo': 123
        })

        self.assertIn('@var: 1', viz)
        self.assertIn('@mimi: $pop', viz)
        self.assertIn('@momo: 123', viz)

    def test_style_dict_variables(self):
        """vis.Style.compute_viz should return the dict viz with the variables"""
        style = vis.Style({
            'vars': {
                'var': 1
            }
        })
        viz = style.compute_viz('line', {
            'mimi': '$pop',
            'momo': 123
        })

        self.assertIn('@var: 1', viz)
        self.assertIn('@mimi: $pop', viz)
        self.assertIn('@momo: 123', viz)

    def test_wrong_attribute(self):
        """vis.Style should raise an error if style property is not valid"""
        with self.assertRaises(ValueError):
            vis.Style({'wrong': 'red'}).compute_viz('point')
