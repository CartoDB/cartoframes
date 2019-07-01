import unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from cartoframes.viz import helpers, Source


class TestSizeContinuousLayerHelper(unittest.TestCase):
    def test_helpers(self):
        "should be defined"
        self.assertNotEqual(helpers.size_continuous_layer, None)

    def test_size_continuous_layer(self):
        "should create a layer with the proper attributes"
        layer = helpers.size_continuous_layer(
            source='sf_neighborhoods',
            value='name'
        )

        self.assertNotEqual(layer.style, None)
        self.assertEqual(layer.style._style['point']['width'],
                         'ramp(linear(sqrt($name), sqrt(globalMin($name)), sqrt(globalMax($name))), [2, 40])')
        self.assertEqual(layer.style._style['line']['width'], 'ramp(linear($name), [1, 10])')
        self.assertEqual(layer.style._style['point']['color'], 'opacity(#FFB927, 0.8)')
        self.assertEqual(layer.style._style['point']['strokeColor'], 'opacity(#222,ramp(linear(zoom(),0,18),[0,0.6]))')
        self.assertEqual(layer.style._style['line']['color'], 'opacity(#4CC8A3, 0.8)')
        self.assertNotEqual(layer.popup, None)
        self.assertEqual(layer.popup._hover, [{
            'title': 'name',
            'value': '$name'
        }])

        self.assertNotEqual(layer.legend, None)
        self.assertEqual(layer.legend._type['point'], 'size-continuous-point')
        self.assertEqual(layer.legend._type['line'], 'size-continuous-line')
        self.assertEqual(layer.legend._title, 'name')
        self.assertEqual(layer.legend._description, '')

    def test_size_continuous_layer_point(self):
        "should create a point type layer"
        layer = helpers.size_continuous_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            size=[10, 20],
            color='blue'
        )

        self.assertEqual(
            layer.style._style['point']['width'],
            'ramp(linear(sqrt($name), sqrt(globalMin($name)), sqrt(globalMax($name))), [10, 20])'
        )
        self.assertEqual(
            layer.style._style['point']['color'],
            'opacity(blue, 0.8)'
        )

    def test_size_continuous_layer_line(self):
        "should create a line type layer"
        Source._get_geom_type = Mock(return_value='line')

        layer = helpers.size_continuous_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            size=[10, 20],
            color='blue'
        )

        self.assertEqual(
            layer.style._style['line']['width'],
            'ramp(linear($name), [10, 20])'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'opacity(blue, 0.8)'
        )
