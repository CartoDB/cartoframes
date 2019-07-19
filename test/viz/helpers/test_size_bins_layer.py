import unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from cartoframes.viz import helpers, Source


class TestSizeBinsLayerHelper(unittest.TestCase):
    def test_helpers(self):
        "should be defined"
        self.assertNotEqual(helpers.size_bins_layer, None)

    def test_size_bins_layer(self):
        "should create a layer with the proper attributes"
        Source._get_geom_type = Mock(return_value='point')

        layer = helpers.size_bins_layer(
            source='sf_neighborhoods',
            value='name'
        )

        self.assertNotEqual(layer.style, None)
        self.assertEqual(layer.style._style['point']['width'], 'ramp(globalQuantiles($name, 5), [2, 14])')
        self.assertEqual(layer.style._style['line']['width'], 'ramp(globalQuantiles($name, 5), [1, 10])')
        self.assertEqual(layer.style._style['point']['color'], 'opacity(#EE4D5A, 0.8)')
        self.assertEqual(layer.style._style['line']['color'], 'opacity(#4CC8A3, 0.8)')
        self.assertNotEqual(layer.popup, None)
        self.assertEqual(layer.popup._hover, [{
            'title': 'name',
            'value': '$name'
        }])

        self.assertNotEqual(layer.legend, None)
        self.assertEqual(layer.legend._type['point'], 'size-bins-point')
        self.assertEqual(layer.legend._type['line'], 'size-bins-line')
        self.assertEqual(layer.legend._title, 'name')
        self.assertEqual(layer.legend._description, '')
        self.assertEqual(layer.legend._footer, '')

    def test_size_bins_layer_point(self):
        "should create a point type layer"
        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            bins=3,
            size=[10, 20],
            color='blue'
        )

        self.assertEqual(
            layer.style._style['point']['width'],
            'ramp(globalQuantiles($name, 3), [10, 20])'
        )
        self.assertEqual(
            layer.style._style['point']['color'],
            'opacity(blue, 0.8)'
        )

    def test_size_bins_layer_line(self):
        "should create a line type layer"
        Source._get_geom_type = Mock(return_value='line')

        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            bins=3,
            size=[10, 20],
            color='blue'
        )

        self.assertEqual(
            layer.style._style['line']['width'],
            'ramp(globalQuantiles($name, 3), [10, 20])'
        )
        self.assertEqual(
            layer.style._style['line']['color'],
            'opacity(blue, 0.8)'
        )

    def test_size_bins_layer_method(self):
        "should apply the classification method"
        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            method='quantiles'
        )

        self.assertEqual(
            layer.style._style['point']['width'],
            'ramp(globalQuantiles($name, 5), [2, 14])'
        )
        self.assertEqual(
            layer.style._style['line']['width'],
            'ramp(globalQuantiles($name, 5), [1, 10])'
        )

        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            method='equal'
        )

        self.assertEqual(
            layer.style._style['point']['width'],
            'ramp(globalEqIntervals($name, 5), [2, 14])'
        )
        self.assertEqual(
            layer.style._style['line']['width'],
            'ramp(globalEqIntervals($name, 5), [1, 10])'
        )

        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            method='stdev'
        )

        self.assertEqual(
            layer.style._style['point']['width'],
            'ramp(globalStandardDev($name, 5), [2, 14])'
        )
        self.assertEqual(
            layer.style._style['line']['width'],
            'ramp(globalStandardDev($name, 5), [1, 10])'
        )

        msg = 'Available methods are: "quantiles", "equal", "stdev".'
        with self.assertRaisesRegexp(ValueError, msg):
            helpers.size_bins_layer(
                'sf_neighborhoods',
                'name',
                method='wrong'
            )

    def test_size_bins_layer_breaks(self):
        "should apply buckets if breaks are passed"
        Source._get_geom_type = Mock(return_value='point')

        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            breaks=[0, 1, 2]
        )

        self.assertEqual(
            layer.style._style['point']['width'],
            'ramp(buckets($name, [0, 1, 2]), [2, 14])'
        )
        self.assertEqual(
            layer.style._style['line']['width'],
            'ramp(buckets($name, [0, 1, 2]), [1, 10])'
        )

    def test_size_bins_layer_legend(self):
        "should show/hide the legend"
        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            legend=False
        )

        self.assertEqual(layer.legend._type, '')
        self.assertEqual(layer.legend._title, '')

        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            legend=True
        )

        self.assertEqual(layer.legend._type, {
            'point': 'size-bins-point',
            'line': 'size-bins-line',
            'polygon': 'size-bins-polygon'
        })
        self.assertEqual(layer.legend._title, 'name')

    def test_size_bins_layer_popup(self):
        "should show/hide the popup"
        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            popup=False
        )

        self.assertEqual(layer.popup._hover, [])

        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            popup=True
        )

        self.assertEqual(layer.popup._hover, [{
            'title': 'name',
            'value': '$name'
        }])

    def test_size_bins_layer_widget(self):
        "should show/hide the widget"
        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            widget=False
        )

        self.assertEqual(layer.widgets._widgets, [])

        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            widget=True
        )

        self.assertEqual(layer.widgets._widgets[0]._type, 'histogram')
        self.assertEqual(layer.widgets._widgets[0]._title, 'Distribution')

    def test_size_bins_layer_animate(self):
        "should animate a property and disable the popups"
        layer = helpers.size_bins_layer(
            'sf_neighborhoods',
            'name',
            animate='time'
        )

        self.assertEqual(layer.popup._hover, [])
        self.assertEqual(layer.widgets._widgets[0]._type, 'time-series')
        self.assertEqual(layer.widgets._widgets[0]._title, 'Animation')
        self.assertEqual(layer.widgets._widgets[0]._value, 'time')
