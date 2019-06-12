import unittest
from unittest.mock import Mock
from cartoframes.viz import helpers, Source


class TestColorCategoryLayerHelper(unittest.TestCase):
    def test_helpers(self):
        "should be defined"
        self.assertNotEqual(helpers.color_category_layer, None)

    def test_color_category_layer(self):
        "should create a layer with the proper attributes"
        layer = helpers.color_category_layer(
            source='sf_neighborhoods',
            value='name',
            title='Neighborhoods'
        )

        self.assertNotEqual(layer.style, None)
        self.assertEqual(layer.style._style['point']['color'], 'ramp(top($name, 11), bold)')
        self.assertNotEqual(layer.popup, None)
        self.assertEqual(layer.popup._hover, [{
            'title': 'Neighborhoods',
            'value': '$name'
        }])

        self.assertNotEqual(layer.legend, None)
        self.assertEqual(layer.legend._type, 'color-category')
        self.assertEqual(layer.legend._title, 'Neighborhoods')
        self.assertEqual(layer.legend._description, '')

    def test_color_category_layer_point(self):
        "should create a point type layer"
        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            top=5,
            palette='prism'
        )

        self.assertEqual(
            layer.style._style['point']['color'],
            'ramp(top($name, 5), prism)'
        )

        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            cat=['A', 'B'],
            palette='[red, blue]'
        )

        self.assertEqual(
            layer.style._style['point']['color'],
            "ramp(buckets($name, ['A', 'B']), [red, blue])"
        )

    def test_color_category_layer_line(self):
        "should create a line type layer"
        Source._get_geom_type = Mock(return_value='line')

        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            top=5,
            palette='prism'
        )

        self.assertEqual(
            layer.style._style['line']['color'],
            'ramp(top($name, 5), prism)'
        )

        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            cat=['A', 'B'],
            palette='[red, blue]'
        )

        self.assertEqual(
            layer.style._style['line']['color'],
            "ramp(buckets($name, ['A', 'B']), [red, blue])"
        )

    def test_color_category_layer_polygon(self):
        "should create a polygon type layer"
        Source._get_geom_type = Mock(return_value='polygon')

        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            top=5,
            palette='prism'
        )

        self.assertEqual(
            layer.style._style['polygon']['color'],
            'opacity(ramp(top($name, 5), prism), 0.9)'
        )

        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            cat=['A', 'B'],
            palette='[red, blue]'
        )

        self.assertEqual(
            layer.style._style['polygon']['color'],
            "opacity(ramp(buckets($name, ['A', 'B']), [red, blue]), 0.9)"
        )
