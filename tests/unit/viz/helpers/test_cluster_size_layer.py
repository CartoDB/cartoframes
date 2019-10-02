import unittest
from carto.exceptions import CartoException
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from cartoframes.viz import helpers, Source


class TestClusterSizeLayerHelper(unittest.TestCase):
    def setUp(self):
        self.orig_compute_query_bounds = Source._compute_query_bounds
        Source._compute_query_bounds = Mock(return_valye=None)

    def tearDown(self):
        Source._compute_query_bounds = self.orig_compute_query_bounds

    def test_helpers(self):
        "should be defined"
        self.assertNotEqual(helpers.cluster_size_layer, None)

    def test_cluster_size_layer(self):
        "should create a layer with the proper attributes"
        Source._get_geom_type = Mock(return_value='point')

        layer = helpers.cluster_size_layer(
            source='sf_neighborhoods',
            value='name'
        )

        self.assertNotEqual(layer.style, None)
        self.assertEqual(
            layer.style._style['point']['width'],
            'ramp(linear(clusterCount(), viewportMIN(clusterCount()), viewportMAX(clusterCount())), [4.0, 16.0, 32])'
        )
        self.assertEqual(layer.style._style['point']['color'],
                         'opacity(#FFB927, 0.8)')
        self.assertEqual(layer.style._style['point']['strokeColor'],
                         'opacity(#222,ramp(linear(zoom(),0,18),[0,0.6]))')
        self.assertEqual(layer.style._style['point']['filter'], '1')
        self.assertEqual(layer.style._style['point']['resolution'], '32')
        self.assertNotEqual(layer.popup, None)
        self.assertEqual(layer.popup._hover, [{
            'title': 'count',
            'value': 'clusterCount()'
        }])

        self.assertNotEqual(layer.legend, None)
        self.assertEqual(layer.legend._type['point'], 'size-continuous-point')
        self.assertEqual(layer.legend._title, 'count')
        self.assertEqual(layer.legend._description, '')
        self.assertEqual(layer.legend._footer, '')

    def test_valid_operation(self):
        """cluster_size_layer should raise an error if the operation is invalid"""

        msg = '"invalid" is not a valid operation. Valid operations are count, min, max, avg, sum'
        with self.assertRaises(CartoException, msg=msg):
            helpers.cluster_size_layer(
                source='sf_neighborhoods',
                value='name',
                operation='invalid'
            )
