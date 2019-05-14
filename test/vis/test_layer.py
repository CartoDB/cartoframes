import unittest
from cartoframes import vis


class TestLayers(unittest.TestCase):
    def test_is_layer_defined(self):
        self.assertNotEqual(vis.Layer, None)

    def test_initialization_objects(self):
        """should initialize layer attributes"""
        layer = vis.Layer(vis.Source('layer_source'), vis.Style())

        self.assertEqual(layer.orig_query, 'SELECT * FROM layer_source')
        self.assertFalse(layer.is_basemap)
        self.assertEqual(layer.style, '')
        self.assertEqual(layer.viz, '')
        self.assertIsNone(layer.interactivity)
        self.assertIsNone(layer.legend)

    def test_initialization_simple(self):
        """should initialize layer attributes"""
        layer = vis.Layer('layer_source', '')

        self.assertEqual(layer.orig_query, 'SELECT * FROM layer_source')
        self.assertFalse(layer.is_basemap)
        self.assertEqual(layer.style, '')
        self.assertEqual(layer.viz, '')
        self.assertIsNone(layer.interactivity)
        self.assertIsNone(layer.legend)


class TestLayersStyle(unittest.TestCase):
    def test_style_dict(self):
        """should set the style when it is a dict"""
        layer = vis.Layer(
            'layer_source',
            {
                'vars': {
                    'grad': '[red, green, blue]'
                },
                'color': 'blue',
                'width': 10,
                'strokeColor': 'black',
                'strokeWidth': 1
            }
        )

        self.assertTrue(isinstance(layer.style, vis.Style))
        self.assertTrue('@grad: [red, green, blue]' in layer.viz)
        self.assertTrue('color: blue' in layer.viz)
        self.assertTrue('width: 10' in layer.viz)
        self.assertTrue('strokeColor: black' in layer.viz)
        self.assertTrue('strokeWidth: 1' in layer.viz)

    def test_style_str(self):
        """should set the style when it is a dict"""
        layer = vis.Layer(
            'layer_source',
            """
                @grad: [red, green, blue]
                color: blue
                width: 10
                strokeColor: black
                strokeWidth: 1
            """
        )

        self.assertTrue(isinstance(layer.style, vis.Style))
        self.assertTrue('@grad: [red, green, blue]' in layer.viz)
        self.assertTrue('color: blue' in layer.viz)
        self.assertTrue('width: 10' in layer.viz)
        self.assertTrue('strokeColor: black' in layer.viz)
        self.assertTrue('strokeWidth: 1' in layer.viz)

    @raises(ValueError)
    def test_style_dict_valid_properties(self):
        """should set only the valid properties"""
        layer = vis.Layer(
            'layer_source',
            {
                'invalid': 1
            }
        )
