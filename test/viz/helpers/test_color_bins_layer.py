import unittest
from unittest.mock import Mock
from cartoframes.viz import helpers, Source


class TestHelpers(unittest.TestCase):
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
        self.assertEqual(layer.style._style['point']['color'], 'ramp(globalQuantiles($name, 5), reverse(purpor))')
        self.assertNotEqual(layer.popup, None)
        self.assertEqual(layer.popup._hover, [{
            'label': 'name',
            'value': '$name'
        }])
        
        self.assertNotEqual(layer.legend, None)
        self.assertEqual(layer.legend['type'], 'basic')
        self.assertEqual(layer.legend['ramp'], 'color')
        self.assertEqual(layer.legend['heading'], 'name')
        self.assertEqual(layer.legend['description'], '')

    
    def test_color_bins_layer_point(self):
        "should create a point type layer"
        
        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            bins=3,
            palette='prism',
            title='Neighborhoods'
        )

        self.assertEqual(layer.style._style['point']['color'], 'ramp(globalQuantiles($name, 3), reverse(prism))')

    def test_color_bins_layer_line(self):
        "should create a line type layer"

        Source._get_geom_type = Mock(return_value='line')
        source = Source('sf_neighborhoods')

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            bins=3,
            palette='prism',
            title='Neighborhoods'
        )

        self.assertEqual(layer.style._style['point']['color'], 'ramp(globalQuantiles($name, 3), reverse(prism))')
    
    def test_color_bins_layer_polygon(self):
        "should create a polygon type layer"

        Source._get_geom_type = Mock(return_value='polygon')
        source = Source('sf_neighborhoods')

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            bins=3,
            palette='prism',
            title='Neighborhoods'
        )
        self.assertEqual(layer.style._style['polygon']['color'], 'opacity(ramp(globalQuantiles($name, 3), reverse(prism)), 0.9)')