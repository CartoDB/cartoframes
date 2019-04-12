import unittest
from cartoframes import carto_vl


class TestLayers(unittest.TestCase):
    def test_is_layer_defined(self):
        self.assertNotEqual(carto_vl.Layer, None)

    def test_is_local_layer_defined(self):
        self.assertNotEqual(carto_vl.LocalLayer, None)

    def test_is_query_layer_defined(self):
        self.assertNotEqual(carto_vl.QueryLayer, None)

    def test_initialization(self):
        """should initialize layer attributes"""
        carto_layer = carto_vl.Layer('layer_source')

        self.assertEqual(carto_layer.orig_query, 'SELECT * FROM layer_source')
        self.assertFalse(carto_layer.is_basemap)
        self.assertEqual(carto_layer.style, '')
        self.assertEqual(carto_layer.viz, '')
        self.assertIsNone(carto_layer.variables)
        self.assertIsNone(carto_layer.interactivity)
        self.assertIsNone(carto_layer.legend)


class TestLayersStyle(unittest.TestCase):
    def test_style_dict(self):
        """should set the style when it is a dict"""
        carto_layer = carto_vl.Layer(
            'layer_source',
            style={
                'color': 'blue',
                'width': 10,
                'stroke-color': 'black',
                'stroke-width': 1
            }
        )

        self.assertTrue('color: blue' in carto_layer.viz)
        self.assertTrue('width: 10' in carto_layer.viz)
        self.assertTrue('strokeColor: black' in carto_layer.viz)
        self.assertTrue('strokeWidth: 1' in carto_layer.viz)

    def test_style_dict_valid_properties(self):
        """should set only the valid properties"""
        carto_layer = carto_vl.Layer(
            'layer_source',
            style={
                'invalid': 1
            }
        )
        self.assertFalse('invalid: 1' in carto_layer.viz)

    def test_style_list(self):
        """should set the style when it is a dict"""
        carto_layer = carto_vl.Layer(
            'layer_source',
            style=[
                ['color', 'blue'],
                ['width', 10],
                ['stroke-color', 'black'],
                ['stroke-width', 1]
            ]
        )

        self.assertTrue('color: blue' in carto_layer.viz)
        self.assertTrue('width: 10' in carto_layer.viz)
        self.assertTrue('strokeColor: black' in carto_layer.viz)
        self.assertTrue('strokeWidth: 1' in carto_layer.viz)

    def test_style_list_valid_properties(self):
        """should set only the valid properties"""
        carto_layer = carto_vl.Layer(
            'layer_source',
            style=[
                ['invalid', 1]
            ]
        )
        self.assertFalse('invalid: 1' in carto_layer.viz)


class TestLayersVariables(unittest.TestCase):
    def test_variables_dict(self):
        """should set the style when it is a dict"""
        carto_layer = carto_vl.Layer(
            'layer_source',
            variables={
                'var_color': 'blue',
                'var_width': 10
            }
        )

        self.assertTrue('@var_color: blue' in carto_layer.viz)
        self.assertTrue('@var_width: 10' in carto_layer.viz)

    def test_style_list(self):
        """should set the style when it is a dict"""
        carto_layer = carto_vl.Layer(
            'layer_source',
            variables=[
                ['var_color', 'blue'],
                ['var_width', 10]
            ]
        )

        self.assertTrue('@var_color: blue' in carto_layer.viz)
        self.assertTrue('@var_width: 10' in carto_layer.viz)
