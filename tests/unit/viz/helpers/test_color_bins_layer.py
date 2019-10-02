import unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from cartoframes.viz import helpers, Source


class TestColorBinsLayerHelper(unittest.TestCase):
    def setUp(self):
        self.orig_compute_query_bounds = Source._compute_query_bounds
        Source._compute_query_bounds = Mock(return_valye=None)

    def tearDown(self):
        Source._compute_query_bounds = self.orig_compute_query_bounds

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
        self.assertEqual(layer.style._style['point']['color'], 'opacity(ramp(globalQuantiles($name, 5), purpor),1)')
        self.assertEqual(layer.style._style['line']['color'], 'opacity(ramp(globalQuantiles($name, 5), purpor),1)')
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
            'opacity(ramp(globalQuantiles($name, 3), prism),1)'
        )

    def test_color_bins_layer_line(self):
        "should create a line type layer"
        Source._get_geom_type = Mock(return_value='line')

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            bins=3,
            palette='[blue,#F00]'
        )

        self.assertEqual(
            layer.style._style['line']['color'],
            'opacity(ramp(globalQuantiles($name, 3), [blue,#F00]),1)'
        )

    def test_color_bins_layer_polygon(self):
        "should create a polygon type layer"
        Source._get_geom_type = Mock(return_value='polygon')

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            bins=3,
            palette=['blue', '#F00']
        )

        self.assertEqual(
            layer.style._style['polygon']['color'],
            'opacity(ramp(globalQuantiles($name, 3), [blue,#F00]), 0.9)'
        )

    def test_color_bins_layer_method(self):
        "should apply the classification method"
        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            method='quantiles'
        )

        self.assertEqual(
            layer.style._style['point']['color'],
            'opacity(ramp(globalQuantiles($name, 5), purpor),1)'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'opacity(ramp(globalQuantiles($name, 5), purpor),1)'
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
            'opacity(ramp(globalEqIntervals($name, 5), purpor),1)'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'opacity(ramp(globalEqIntervals($name, 5), purpor),1)'
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
            'opacity(ramp(globalStandardDev($name, 5), temps),1)'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'opacity(ramp(globalStandardDev($name, 5), temps),1)'
        )
        self.assertEqual(
            layer.style._style['polygon']['color'],
            'opacity(ramp(globalStandardDev($name, 5), temps), 0.9)'
        )

        msg = 'Available methods are: "quantiles", "equal", "stdev".'
        with self.assertRaisesRegexp(ValueError, msg):
            helpers.color_bins_layer(
                'sf_neighborhoods',
                'name',
                method='wrong'
            )

    def test_color_bins_layer_breaks(self):
        "should apply buckets if breaks are passed"
        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            breaks=[0, 1, 2]
        )

        self.assertEqual(
            layer.style._style['point']['color'],
            'opacity(ramp(buckets($name, [0, 1, 2]), purpor),1)'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'opacity(ramp(buckets($name, [0, 1, 2]), purpor),1)'
        )
        self.assertEqual(
            layer.style._style['polygon']['color'],
            'opacity(ramp(buckets($name, [0, 1, 2]), purpor), 0.9)'
        )

    def test_color_bins_layer_legend(self):
        "should show/hide the legend"
        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            legend=False
        )

        self.assertEqual(layer.legend._type, '')
        self.assertEqual(layer.legend._title, '')

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            legend=True
        )

        self.assertEqual(layer.legend._type, {
            'point': 'color-bins-point',
            'line': 'color-bins-line',
            'polygon': 'color-bins-polygon'
        })
        self.assertEqual(layer.legend._title, 'name')

    def test_color_bins_layer_popup(self):
        "should show/hide the popup"
        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            popup=False
        )

        self.assertEqual(layer.popup._hover, [])

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            popup=True
        )

        self.assertEqual(layer.popup._hover, [{
            'title': 'name',
            'value': '$name'
        }])

    def test_color_bins_layer_widget(self):
        "should show/hide the widget"
        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            widget=False
        )

        self.assertEqual(layer.widgets._widgets, [])

        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            widget=True
        )

        self.assertEqual(layer.widgets._widgets[0]._type, 'histogram')
        self.assertEqual(layer.widgets._widgets[0]._title, 'Distribution')

    def test_color_bins_layer_animate(self):
        "should animate a property and disable the popups"
        layer = helpers.color_bins_layer(
            'sf_neighborhoods',
            'name',
            animate='time'
        )

        self.assertEqual(layer.popup._hover, [])
        self.assertEqual(layer.widgets._widgets[0]._type, 'time-series')
        self.assertEqual(layer.widgets._widgets[0]._title, 'Animation')
        self.assertEqual(layer.widgets._widgets[0]._value, 'time')
