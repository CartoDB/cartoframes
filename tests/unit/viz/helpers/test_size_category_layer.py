from cartoframes.viz import helpers
from cartoframes.auth import Credentials

from . import setup_mocks
from ..utils import build_cartodataframe


class TestSizeCategoryLayerHelper(object):
    def setup_method(self):
        self.source = build_cartodataframe([0], [0], ['name', 'time'])

    def test_helpers(self):
        "should be defined"
        assert helpers.size_category_layer is not None

    def test_size_category_layer(self, mocker):
        "should create a layer with the proper attributes"
        setup_mocks(mocker)
        layer = helpers.size_category_layer(
            source='SELECT * FROM faketable',
            value='name',
            title='Neighborhoods',
            credentials=Credentials('fakeuser')
        )

        assert layer.style is not None
        assert layer.style._style['point']['width'] == 'ramp(top($name, 5), [2, 20])'
        assert layer.style._style['line']['width'] == 'ramp(top($name, 5), [1, 10])'
        assert layer.style._style['point']['color'] == 'opacity(#F46D43, 0.8)'
        assert layer.style._style['line']['color'] == 'opacity(#4CC8A3, 0.8)'

        assert layer.popup is not None
        assert layer.popup._hover == [{
            'title': 'Neighborhoods',
            'value': '$name'
        }]

        assert layer.legend is not None
        assert layer.legend._type['point'] == 'size-category-point'
        assert layer.legend._type['line'] == 'size-category-line'
        assert layer.legend._title == 'Neighborhoods'
        assert layer.legend._description == ''
        assert layer.legend._footer == ''

    def test_size_category_layer_point(self, mocker):
        "should create a point type layer"
        setup_mocks(mocker)
        layer = helpers.size_category_layer(
            self.source,
            'name',
            'Neighborhoods',
            top=5,
            size=[10, 20],
            color='blue'
        )

        assert layer.style._style['point']['width'] == 'ramp(top($name, 5), [10, 20])'
        assert layer.style._style['point']['color'] == 'opacity(blue, 0.8)'

        layer = helpers.size_category_layer(
            self.source,
            'name',
            'Neighborhoods',
            cat=['A', 'B'],
            size=[10, 20],
            color='blue'
        )

        assert layer.style._style['point']['width'] == "ramp(buckets($name, ['A', 'B']), [10, 20])"
        assert layer.style._style['point']['color'] == 'opacity(blue, 0.8)'

    def test_size_category_layer_line(self, mocker):
        "should create a line type layer"
        setup_mocks(mocker, 'line')
        layer = helpers.size_category_layer(
            self.source,
            'name',
            'Neighborhoods',
            top=5,
            size=[10, 20],
            color='blue'
        )

        assert layer.style._style['line']['width'] == 'ramp(top($name, 5), [10, 20])'
        assert layer.style._style['line']['color'] == 'opacity(blue, 0.8)'

        layer = helpers.size_category_layer(
            self.source,
            'name',
            'Neighborhoods',
            cat=['A', 'B'],
            size=[10, 20],
            color='blue'
        )

        assert layer.style._style['line']['width'] == "ramp(buckets($name, ['A', 'B']), [10, 20])"
        assert layer.style._style['line']['color'] == 'opacity(blue, 0.8)'

    def test_size_category_layer_legend(self, mocker):
        "should show/hide the legend"
        setup_mocks(mocker)
        layer = helpers.size_category_layer(
            self.source,
            'name',
            legend=False
        )

        assert layer.legend._type == ''
        assert layer.legend._title == ''

        layer = helpers.size_category_layer(
            self.source,
            'name',
            legend=True
        )

        assert layer.legend._type == {
            'point': 'size-category-point',
            'line': 'size-category-line',
            'polygon': 'size-category-polygon'
        }
        assert layer.legend._title == 'name'

    def test_size_category_layer_popup(self, mocker):
        "should show/hide the popup"
        setup_mocks(mocker)
        layer = helpers.size_category_layer(
            self.source,
            'name',
            popup=False
        )

        assert layer.popup._hover == []

        layer = helpers.size_category_layer(
            self.source,
            'name',
            popup=True
        )

        assert layer.popup._hover, [{
            'title': 'name',
            'value': '$name'
        }]

    def test_size_category_layer_widget(self, mocker):
        "should show/hide the widget"
        setup_mocks(mocker)
        layer = helpers.size_category_layer(
            self.source,
            'name',
            widget=False
        )

        assert layer.widgets._widgets == []

        layer = helpers.size_category_layer(
            self.source,
            'name',
            widget=True
        )

        assert layer.widgets._widgets[0]._type == 'category'
        assert layer.widgets._widgets[0]._title == 'Categories'

    def test_size_category_layer_animate(self, mocker):
        "should animate a property and disable the popups"
        setup_mocks(mocker)
        layer = helpers.size_category_layer(
            self.source,
            'name',
            animate='time'
        )

        assert layer.popup._hover == []
        assert layer.widgets._widgets[0]._type == 'time-series'
        assert layer.widgets._widgets[0]._title == 'Animation'
        assert layer.widgets._widgets[0]._value == 'time'
