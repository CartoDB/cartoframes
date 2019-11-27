from cartoframes.viz import helpers
from cartoframes.auth import Credentials

from . import setup_mocks
from ..utils import build_cartodataframe


class TestColorCategoryLayerHelper(object):
    def setup_method(self):
        self.source = build_cartodataframe([0], [0], ['name', 'time'])

    def test_helpers(self):
        "should be defined"
        assert helpers.color_category_layer is not None

    def test_color_category_layer(self, mocker):
        "should create a layer with the proper attributes"
        setup_mocks(mocker)
        layer = helpers.color_category_layer(
            source='SELECT * FROM faketable',
            value='name',
            title='Neighborhoods',
            credentials=Credentials('fakeuser')
        )

        assert layer.style is not None
        assert layer.style._style['point']['color'] == 'opacity(ramp(top($name, 11), bold),1)'
        assert layer.style._style['line']['color'] == 'opacity(ramp(top($name, 11), bold),1)'
        assert layer.style._style['polygon']['color'] == 'opacity(ramp(top($name, 11), bold), 0.9)'

        assert layer.popup is not None
        assert layer.popup._hover == [{
            'title': 'Neighborhoods',
            'value': '$name'
        }]

        assert layer.legend is not None
        assert layer.legend._type['point'] == 'color-category-point'
        assert layer.legend._type['line'] == 'color-category-line'
        assert layer.legend._type['polygon'] == 'color-category-polygon'
        assert layer.legend._title, 'Neighborhoods'
        assert layer.legend._description == ''
        assert layer.legend._footer == ''

    def test_color_category_layer_point(self, mocker):
        "should create a point type layer"
        setup_mocks(mocker)
        layer = helpers.color_category_layer(
            self.source,
            'name',
            'Neighborhoods',
            top=5,
            palette='prism'
        )

        assert layer.style._style['point']['color'] == 'opacity(ramp(top($name, 5), prism),1)'

        layer = helpers.color_category_layer(
            self.source,
            'name',
            'Neighborhoods',
            cat=['A', 'B'],
            palette=['red', 'blue']
        )

        assert layer.style._style['point']['color'] == "opacity(ramp(buckets($name, ['A', 'B']), [red,blue]),1)"

    def test_color_category_layer_line(self, mocker):
        "should create a line type layer"
        setup_mocks(mocker, 'line')
        layer = helpers.color_category_layer(
            self.source,
            'name',
            'Neighborhoods',
            top=5,
            palette='prism'
        )

        assert layer.style._style['line']['color'] == 'opacity(ramp(top($name, 5), prism),1)'

        layer = helpers.color_category_layer(
            self.source,
            'name',
            'Neighborhoods',
            cat=['A', 'B'],
            palette=['red', 'blue']
        )

        assert layer.style._style['line']['color'] == "opacity(ramp(buckets($name, ['A', 'B']), [red,blue]),1)"

    def test_color_category_layer_polygon(self, mocker):
        "should create a polygon type layer"
        setup_mocks(mocker, 'polygon')
        layer = helpers.color_category_layer(
            self.source,
            'name',
            'Neighborhoods',
            top=5,
            palette='prism'
        )

        assert layer.style._style['polygon']['color'] == 'opacity(ramp(top($name, 5), prism), 0.9)'

        layer = helpers.color_category_layer(
            self.source,
            'name',
            'Neighborhoods',
            cat=['A', 'B'],
            palette=['red', 'blue']
        )

        assert layer.style._style['polygon']['color'] == "opacity(ramp(buckets($name, ['A', 'B']), [red,blue]), 0.9)"

    def test_color_category_layer_legend(self, mocker):
        "should show/hide the legend"
        setup_mocks(mocker)
        layer = helpers.color_category_layer(
            self.source,
            'name',
            legend=False
        )

        assert layer.legend._type == ''
        assert layer.legend._title == ''

        layer = helpers.color_category_layer(
            self.source,
            'name',
            legend=True
        )

        assert layer.legend._type == {
            'point': 'color-category-point',
            'line': 'color-category-line',
            'polygon': 'color-category-polygon'
        }
        assert layer.legend._title == 'name'

    def test_color_category_layer_popup(self, mocker):
        "should show/hide the popup"
        setup_mocks(mocker)
        layer = helpers.color_category_layer(
            self.source,
            'name',
            popup=False
        )

        assert layer.popup._hover == []

        layer = helpers.color_category_layer(
            self.source,
            'name',
            popup=True
        )

        assert layer.popup._hover == [{
            'title': 'name',
            'value': '$name'
        }]

    def test_color_category_layer_widget(self, mocker):
        "should show/hide the widget"
        setup_mocks(mocker)
        layer = helpers.color_category_layer(
            self.source,
            'name',
            widget=False
        )

        assert layer.widgets._widgets == []

        layer = helpers.color_category_layer(
            self.source,
            'name',
            widget=True
        )

        assert layer.widgets._widgets[0]._type == 'category'
        assert layer.widgets._widgets[0]._title == 'Categories'

    def test_color_category_layer_animate(self, mocker):
        "should animate a property and disable the popups"
        setup_mocks(mocker)
        layer = helpers.color_category_layer(
            self.source,
            'name',
            animate='time'
        )

        assert layer.popup._hover == []
        assert layer.widgets._widgets[0]._type == 'time-series'
        assert layer.widgets._widgets[0]._title == 'Animation'
        assert layer.widgets._widgets[0]._value == 'time'
