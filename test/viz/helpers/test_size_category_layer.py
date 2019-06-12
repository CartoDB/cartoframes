import unittest
from unittest.mock import Mock
from cartoframes.viz import helpers, Source


class TestSizeCategoryLayerHelper(unittest.TestCase):
    def test_helpers(self):
        "should be defined"
        self.assertNotEqual(helpers.size_category_layer, None)

    def test_size_category_layer(self):
        "should create a layer with the proper attributes"
        layer = helpers.size_category_layer(
            source='sf_neighborhoods',
            value='name',
            title='Neighborhoods'
        )

        self.assertNotEqual(layer.style, None)
        self.assertEqual(layer.style._style['point']['width'], 'ramp(top($name, 5), [2, 20])')
        self.assertEqual(layer.style._style['line']['width'], 'ramp(top($name, 5), [1, 10])')
        self.assertEqual(layer.style._style['point']['color'], 'opacity(#F46D43, 0.8)')
        self.assertEqual(layer.style._style['line']['color'], 'opacity(#4CC8A3, 0.8)')
        self.assertNotEqual(layer.popup, None)
        self.assertEqual(layer.popup._hover, [{
            'title': 'Neighborhoods',
            'value': '$name'
        }])

        self.assertNotEqual(layer.legend, None)
        self.assertEqual(layer.legend._type, 'size-category')
        self.assertEqual(layer.legend._title, 'Neighborhoods')
        self.assertEqual(layer.legend._description, '')

    def test_size_category_layer_point(self):
        "should create a point type layer"
        layer = helpers.size_category_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            top=5,
            size=[10, 20],
            color='blue'
        )

        self.assertEqual(
            layer.style._style['point']['width'],
            'ramp(top($name, 5), [10, 20])'
        )
        self.assertEqual(
            layer.style._style['point']['color'],
            'opacity(blue, 0.8)'
        )

        layer = helpers.size_category_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            cat=['A', 'B'],
            size=[10, 20],
            color='blue'
        )

        self.assertEqual(
            layer.style._style['point']['width'],
            "ramp(buckets($name, ['A', 'B']), [10, 20])"
        )
        self.assertEqual(
            layer.style._style['point']['color'],
            'opacity(blue, 0.8)'
        )

    def test_size_category_layer_line(self):
        "should create a line type layer"
        Source._get_geom_type = Mock(return_value='line')

        layer = helpers.size_category_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            top=5,
            size=[10, 20],
            color='blue'
        )

        self.assertEqual(
            layer.style._style['line']['width'],
            'ramp(top($name, 5), [10, 20])'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'opacity(blue, 0.8)'
        )

        layer = helpers.size_category_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            cat=['A', 'B'],
            size=[10, 20],
            color='blue'
        )

        self.assertEqual(
            layer.style._style['line']['width'],
            "ramp(buckets($name, ['A', 'B']), [10, 20])"
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'opacity(blue, 0.8)'
        )
