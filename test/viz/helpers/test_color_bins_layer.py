import unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from cartoframes.viz import helpers, Source


class TestColorBinsLayerHelper(unittest.TestCase):
    def test_helpers(self):
        "should be defined"
        self.assertNotEqual(helpers.color_bins_layer, None)

    def test_color_bins_layer(self):
        "should create a layer with the proper attributes"
        layer = helpers.color_bins_layer(
            source='sf_neighborhoods',
            value='name'
        )

        self.assertNotEqual(layer.style, None)
        self.assertEqual(layer.style._style['point']['color'], 'ramp(globalQuantiles($name, 5), purpor)')
        self.assertEqual(layer.style._style['line']['color'], 'ramp(globalQuantiles($name, 5), purpor)')
        self.assertEqual(layer.style._style['polygon']['color'],
                         'opacity(ramp(globalQuantiles($name, 5), purpor), 0.9)')
        self.assertNotEqual(layer.popup, None)
        self.assertEqual(layer.popup._hover, [{
            'title': 'name',
            'value': '$name'
        }])

        self.assertNotEqual(layer.legend, None)
        self.assertEqual(layer.legend._type['point'], 'color-bins-point')
        self.assertEqual(layer.legend._type['line'], 'color-bins-line')
        self.assertEqual(layer.legend._type['polygon'], 'color-bins-polygon')
        self.assertEqual(layer.legend._title, 'name')
        self.assertEqual(layer.legend._description, '')
        self.assertEqual(layer.legend._footer, '')

    def test_color_bins_layer_point(self):
        "should create a point type layer"
        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            bins=3,
            palette='prism'
        )
    
        self.assertEqual(
            layer.style._style['point']['color'],
            'ramp(globalQuantiles($name, 3), prism)'
        )

    def test_color_bins_layer_line(self):
        "should create a line type layer"
        Source._get_geom_type = Mock(return_value='line')

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            bins=3,
            palette='prism'
        )

        self.assertEqual(
            layer.style._style['line']['color'],
            'ramp(globalQuantiles($name, 3), prism)'
        )

    def test_color_bins_layer_polygon(self):
        "should create a polygon type layer"
        Source._get_geom_type = Mock(return_value='polygon')

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            bins=3,
            palette='prism'
        )

        self.assertEqual(
            layer.style._style['polygon']['color'],
            'opacity(ramp(globalQuantiles($name, 3), prism), 0.9)'
        )

    def test_color_bins_layer_method(self):
        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            method='quantiles'
        )

        self.assertEqual(
            layer.style._style['point']['color'],
            'ramp(globalQuantiles($name, 5), purpor)'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'ramp(globalQuantiles($name, 5), purpor)'
        )
        self.assertEqual(
            layer.style._style['polygon']['color'],
            'opacity(ramp(globalQuantiles($name, 5), purpor), 0.9)'
        )

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            method='equal'
        )

        self.assertEqual(
            layer.style._style['point']['color'],
            'ramp(globalEqIntervals($name, 5), purpor)'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'ramp(globalEqIntervals($name, 5), purpor)'
        )
        self.assertEqual(
            layer.style._style['polygon']['color'],
            'opacity(ramp(globalEqIntervals($name, 5), purpor), 0.9)'
        )

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            method='stdev'
        )

        self.assertEqual(
            layer.style._style['point']['color'],
            'ramp(globalStandardDev($name, 5), temps)'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'ramp(globalStandardDev($name, 5), temps)'
        )
        self.assertEqual(
            layer.style._style['polygon']['color'],
            'opacity(ramp(globalStandardDev($name, 5), temps), 0.9)'
        )

    def test_color_bins_layer_breaks(self):
        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            breaks=[0, 1, 2]
        )

        self.assertEqual(
            layer.style._style['point']['color'],
            'ramp(buckets($name, [0, 1, 2]), purpor)'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'ramp(buckets($name, [0, 1, 2]), purpor)'
        )
        self.assertEqual(
            layer.style._style['polygon']['color'],
            'opacity(ramp(buckets($name, [0, 1, 2]), purpor), 0.9)'
        )
        
