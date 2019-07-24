import unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from cartoframes.viz import helpers, Source


class TestColorContinuousLayerHelper(unittest.TestCase):
    def setUp(self):
        self.orig_compute_query_bounds = Source._compute_query_bounds
        Source._compute_query_bounds = Mock(return_valye=None)

    def tearDown(self):
        Source._compute_query_bounds = self.orig_compute_query_bounds

    def test_helpers(self):
        "should be defined"
        self.assertNotEqual(helpers.color_continuous_layer, None)

    def test_color_continuous_layer(self):
        "should create a layer with the proper attributes"
        Source._get_geom_type = Mock(return_value='point')

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
        self.assertEqual(layer.legend._footer, '')

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

    def test_color_continuous_layer_legend(self):
        "should show/hide the legend"
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            legend=False
        )

        self.assertEqual(layer.legend._type, '')
        self.assertEqual(layer.legend._title, '')

        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            legend=True
        )

        self.assertEqual(layer.legend._type, {
            'point': 'color-continuous-point',
            'line': 'color-continuous-line',
            'polygon': 'color-continuous-polygon'
        })
        self.assertEqual(layer.legend._title, 'name')

    def test_color_continuous_layer_popup(self):
        "should show/hide the popup"
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            popup=False
        )

        self.assertEqual(layer.popup._hover, [])

        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            popup=True
        )

        self.assertEqual(layer.popup._hover, [{
            'title': 'name',
            'value': '$name'
        }])

    def test_color_continuous_layer_widget(self):
        "should show/hide the widget"
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            widget=False
        )

        self.assertEqual(layer.widgets._widgets, [])

        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            widget=True
        )

        self.assertEqual(layer.widgets._widgets[0]._type, 'histogram')
        self.assertEqual(layer.widgets._widgets[0]._title, 'Distribution')

    def test_color_continuous_layer_animate(self):
        "should animate a property and disable the popups"
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            animate='time'
        )

        self.assertEqual(layer.popup._hover, [])
        self.assertEqual(layer.widgets._widgets[0]._type, 'time-series')
        self.assertEqual(layer.widgets._widgets[0]._title, 'Animation')
        self.assertEqual(layer.widgets._widgets[0]._value, 'time')
