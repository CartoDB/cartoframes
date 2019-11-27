from cartoframes.viz import helpers
from cartoframes.auth import Credentials

from . import setup_mocks
from ..utils import build_cartodataframe


class TestSizeContinuousLayerHelper(object):
    def setup_method(self):
        self.source = build_cartodataframe([0], [0], ['name', 'time'])

    def test_helpers(self):
        "should be defined"
        assert helpers.size_continuous_layer is not None

    def test_size_continuous_layer(self, mocker):
        "should create a layer with the proper attributes"
        setup_mocks(mocker)
        layer = helpers.size_continuous_layer(
            source='SELECT * FROM faketable',
            value='name',
            credentials=Credentials('fakeuser')
        )

        assert layer.style is not None
        assert layer.style._style['point']['width'] == 'ramp(linear(sqrt($name), ' + \
            'sqrt(globalMIN($name)), sqrt(globalMAX($name))), [2, 40])'
        assert layer.style._style['line']['width'] == 'ramp(linear($name, ' + \
            'globalMIN($name), globalMAX($name)), [1, 10])'
        assert layer.style._style['point']['color'] == 'opacity(#FFB927, 0.8)'
        assert layer.style._style['point']['strokeColor'] == 'opacity(#222,ramp(linear(zoom(),0,18),[0,0.6]))'
        assert layer.style._style['line']['color'] == 'opacity(#4CC8A3, 0.8)'

        assert layer.popup is not None
        assert layer.popup._hover, [{
            'title': 'name',
            'value': '$name'
        }]

        assert layer.legend is not None
        assert layer.legend._type['point'] == 'size-continuous-point'
        assert layer.legend._type['line'] == 'size-continuous-line'
        assert layer.legend._title == 'name'
        assert layer.legend._description == ''
        assert layer.legend._footer == ''

    def test_size_continuous_layer_point(self, mocker):
        "should create a point type layer"
        setup_mocks(mocker)
        layer = helpers.size_continuous_layer(
            self.source,
            'name',
            'Neighborhoods',
            size=[10, 20],
            color='blue'
        )

        assert layer.style._style['point']['width'] == 'ramp(linear(sqrt($name), ' + \
            'sqrt(globalMIN($name)), sqrt(globalMAX($name))), [10, 20])'
        assert layer.style._style['point']['color'] == 'opacity(blue, 0.8)'

    def test_size_continuous_layer_line(self, mocker):
        "should create a line type layer"
        setup_mocks(mocker, 'line')
        layer = helpers.size_continuous_layer(
            self.source,
            'name',
            'Neighborhoods',
            size=[10, 20],
            color='blue'
        )

        assert layer.style._style['line']['width'] == 'ramp(linear($name, ' + \
            'globalMIN($name), globalMAX($name)), [10, 20])'
        assert layer.style._style['line']['color'] == 'opacity(blue, 0.8)'

    def test_size_continuous_layer_legend(self, mocker):
        "should show/hide the legend"
        setup_mocks(mocker)
        layer = helpers.size_continuous_layer(
            self.source,
            'name',
            legend=False
        )

        assert layer.legend._type == ''
        assert layer.legend._title == ''

        layer = helpers.size_continuous_layer(
            self.source,
            'name',
            legend=True
        )

        assert layer.legend._type == {
            'point': 'size-continuous-point',
            'line': 'size-continuous-line',
            'polygon': 'size-continuous-polygon'
        }
        assert layer.legend._title == 'name'

    def test_size_continuous_layer_popup(self, mocker):
        "should show/hide the popup"
        setup_mocks(mocker)
        layer = helpers.size_continuous_layer(
            self.source,
            'name',
            popup=False
        )

        assert layer.popup._hover == []

        layer = helpers.size_continuous_layer(
            self.source,
            'name',
            popup=True
        )

        assert layer.popup._hover == [{
            'title': 'name',
            'value': '$name'
        }]

    def test_size_continuous_layer_widget(self, mocker):
        "should show/hide the widget"
        setup_mocks(mocker)
        layer = helpers.size_continuous_layer(
            self.source,
            'name',
            widget=False
        )

        assert layer.widgets._widgets == []

        layer = helpers.size_continuous_layer(
            self.source,
            'name',
            widget=True
        )

        assert layer.widgets._widgets[0]._type == 'histogram'
        assert layer.widgets._widgets[0]._title == 'Distribution'

    def test_size_continuous_layer_animate(self, mocker):
        "should animate a property and disable the popups"
        setup_mocks(mocker)
        layer = helpers.size_continuous_layer(
            self.source,
            'name',
            animate='time'
        )

        assert layer.popup._hover == []
        assert layer.widgets._widgets[0]._type == 'time-series'
        assert layer.widgets._widgets[0]._title == 'Animation'
        assert layer.widgets._widgets[0]._value == 'time'
