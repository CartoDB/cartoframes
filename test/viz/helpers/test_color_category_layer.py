import unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from cartoframes.viz import helpers, Source


class TestColorCategoryLayerHelper(unittest.TestCase):
    def test_helpers(self):
        "should be defined"
        self.assertNotEqual(helpers.color_category_layer, None)

    def test_color_category_layer(self):
        "should create a layer with the proper attributes"
        Source._get_geom_type = Mock(return_value='point')

        layer = helpers.color_category_layer(
            source='sf_neighborhoods',
            value='name',
            title='Neighborhoods'
        )

        self.assertNotEqual(layer.style, None)
        self.assertEqual(layer.style._style['point']['color'], 'ramp(top($name, 11), bold)')
        self.assertEqual(layer.style._style['line']['color'], 'ramp(top($name, 11), bold)')
        self.assertEqual(layer.style._style['polygon']['color'], 'opacity(ramp(top($name, 11), bold), 0.9)')
        self.assertNotEqual(layer.popup, None)
        self.assertEqual(layer.popup._hover, [{
            'title': 'Neighborhoods',
            'value': '$name'
        }])

        self.assertNotEqual(layer.legend, None)
        self.assertEqual(layer.legend._type['point'], 'color-category-point')
        self.assertEqual(layer.legend._type['line'], 'color-category-line')
        self.assertEqual(layer.legend._type['polygon'], 'color-category-polygon')
        self.assertEqual(layer.legend._title, 'Neighborhoods')
        self.assertEqual(layer.legend._description, '')
        self.assertEqual(layer.legend._footer, '')

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

    def test_color_category_layer_legend(self):
        "should show/hide the legend"
        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            legend=False
        )

        self.assertEqual(layer.legend._type, '')
        self.assertEqual(layer.legend._title, '')

        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            legend=True
        )

        self.assertEqual(layer.legend._type, {
            'point': 'color-category-point',
            'line': 'color-category-line',
            'polygon': 'color-category-polygon'
        })
        self.assertEqual(layer.legend._title, 'name')

    def test_color_category_layer_popup(self):
        "should show/hide the popup"
        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            popup=False
        )

        self.assertEqual(layer.popup._hover, [])

        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            popup=True
        )

        self.assertEqual(layer.popup._hover, [{
            'title': 'name',
            'value': '$name'
        }])

    def test_color_category_layer_widget(self):
        "should show/hide the widget"
        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            widget=False
        )

        self.assertEqual(layer.widgets._widgets, [])

        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            widget=True
        )

        self.assertEqual(layer.widgets._widgets[0]._type, 'category')
        self.assertEqual(layer.widgets._widgets[0]._title, 'Categories')


    def test_color_category_layer_animate(self):
        "should animate a property and disable the popups"
        layer = helpers.color_category_layer(
            'sf_neighborhoods',
            'name',
            animate='time'
        )

        self.assertEqual(layer.popup._hover, [])
        self.assertEqual(layer.widgets._widgets[0]._type, 'time-series')
        self.assertEqual(layer.widgets._widgets[0]._title, 'Animation')
        self.assertEqual(layer.widgets._widgets[0]._value, 'time')
