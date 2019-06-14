import unittest
from unittest.mock import Mock
from cartoframes.viz import helpers, Source


class TestColorContinuousLayerHelper(unittest.TestCase):
    def test_helpers(self):
        "should be defined"
        self.assertNotEqual(helpers.color_continuous_layer, None)

    def test_color_continuous_layer(self):
        "should create a layer with the proper attributes"
        layer = helpers.color_continuous_layer(
            source='sf_neighborhoods',
            value='name'
        )

        self.assertNotEqual(layer.style, None)
        self.assertEqual(layer.style._style['point']['color'], 'ramp(linear($name), bluyl)')
        self.assertEqual(layer.style._style['line']['color'], 'ramp(linear($name), bluyl)')
        self.assertEqual(layer.style._style['polygon']['color'], 'opacity(ramp(linear($name), bluyl), 0.9)')
        self.assertNotEqual(layer.popup, None)
        self.assertEqual(layer.popup._hover, [{
            'title': 'name',
            'value': '$name'
        }])

        self.assertNotEqual(layer.legend, None)
        self.assertEqual(layer.legend._type['point'], 'color-continuous-point')
        self.assertEqual(layer.legend._type['line'], 'color-continuous-line')
        self.assertEqual(layer.legend._type['polygon'], 'color-continuous-polygon')
        self.assertEqual(layer.legend._title, 'name')
        self.assertEqual(layer.legend._description, '')

    def test_color_continuous_layer_point(self):
        "should create a point type layer"
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            palette='prism'
        )

        self.assertEqual(
            layer.style._style['point']['color'],
            'ramp(linear($name), prism)'
        )

    def test_color_continuous_layer_line(self):
        "should create a line type layer"
        Source._get_geom_type = Mock(return_value='line')

        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            palette='prism'
        )

        self.assertEqual(
            layer.style._style['line']['color'],
            'ramp(linear($name), prism)'
        )

    def test_color_continuous_layer_polygon(self):
        "should create a polygon type layer"
        Source._get_geom_type = Mock(return_value='polygon')

        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            palette='prism'
        )

        self.assertEqual(
            layer.style._style['polygon']['color'],
            'opacity(ramp(linear($name), prism), 0.9)'
        )
