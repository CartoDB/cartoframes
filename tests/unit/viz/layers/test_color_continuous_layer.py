import pytest

from cartoframes.viz import layers
from cartoframes.auth import Credentials

from . import setup_mocks
from ..utils import build_geodataframe


@pytest.mark.skip(reason="This helper will be removed")
class TestColorContinuousLayerHelper(object):
    def setup_method(self):
        self.source = build_geodataframe([0], [0], ['name', 'time'])

    def test_helpers(self):
        "should be defined"
        assert layers.color_continuous_layer is not None

    def test_color_continuous_layer(self, mocker):
        "should create a layer with the proper attributes"
        setup_mocks(mocker)
        layer = layers.color_continuous_layer(
            source='SELECT * FROM faketable',
            value='name',
            credentials=Credentials('fakeuser')
        )

        assert layer.style is not None
        assert layer.style._style['point']['color'] == 'opacity(ramp(linear($name, ' + \
            'globalMIN($name), globalMAX($name)), bluyl), 1)'
        assert layer.style._style['line']['color'] == 'opacity(ramp(linear($name, ' + \
            'globalMIN($name), globalMAX($name)), bluyl), 1)'
        assert layer.style._style['polygon']['color'] == 'opacity(ramp(linear($name, ' + \
            'globalMIN($name), globalMAX($name)), bluyl), 0.9)'
        assert layer.popups, None

        popup = layer.popups.elements[0]

        assert popup.title == 'name'
        assert popup.value == '$name'
        assert layer.legend is not None
        assert layer.legend._type['point'] == 'color-continuous-point'
        assert layer.legend._type['line'] == 'color-continuous-line'
        assert layer.legend._type['polygon'] == 'color-continuous-polygon'
        assert layer.legend._title == 'name'
        assert layer.legend._description == ''
        assert layer.legend._footer == ''

    def test_color_continuous_layer_point(self, mocker):
        "should create a point type layer"
        setup_mocks(mocker)
        layer = layers.color_continuous_layer(
            self.source,
            'name',
            'Neighborhoods',
            palette='prism'
        )

        assert layer.style._style['point']['color'] == 'opacity(ramp(linear($name, ' + \
            'globalMIN($name), globalMAX($name)), prism), 1)'

    def test_color_continuous_layer_line(self, mocker):
        "should create a line type layer"
        setup_mocks(mocker, 'line')
        layer = layers.color_continuous_layer(
            self.source,
            'name',
            'Neighborhoods',
            palette='[blue,#F00]'
        )

        assert layer.style._style['line']['color'] == 'opacity(ramp(linear($name, ' + \
            'globalMIN($name), globalMAX($name)), [blue,#F00]), 1)'

    def test_color_continuous_layer_polygon(self, mocker):
        "should create a polygon type layer"
        setup_mocks(mocker, 'polygon')
        layer = layers.color_continuous_layer(
            self.source,
            'name',
            'Neighborhoods',
            palette=['blue', '#F00']
        )

        assert layer.style._style['polygon']['color'] == 'opacity(ramp(linear($name, ' + \
            'globalMIN($name), globalMAX($name)), [blue,#F00]), 0.9)'

    def test_color_continuous_layer_legend(self, mocker):
        "should show/hide the legend"
        setup_mocks(mocker)
        layer = layers.color_continuous_layer(
            self.source,
            'name',
            legend=False
        )

        assert layer.legend._type == ''
        assert layer.legend._title == ''

        layer = layers.color_continuous_layer(
            self.source,
            'name',
            legend=True
        )

        assert layer.legend._type == {
            'point': 'color-continuous-point',
            'line': 'color-continuous-line',
            'polygon': 'color-continuous-polygon'
        }
        assert layer.legend._title == 'name'

    def test_color_continuous_layer_popup(self, mocker):
        "should show/hide the popup"
        setup_mocks(mocker)
        layer = layers.color_continuous_layer(
            self.source,
            'name',
            popups=False
        )

        assert len(layer.popups.elements) == 0

        layer = layers.color_continuous_layer(
            self.source,
            'name',
            popups=True
        )

        popup = layer.popups.elements[0]
        assert popup.title == 'name'
        assert popup.value == '$name'

    def test_color_continuous_layer_widget(self, mocker):
        "should show/hide the widget"
        setup_mocks(mocker)
        layer = layers.color_continuous_layer(
            self.source,
            'name',
            widget=False
        )

        assert layer.widgets._widgets == []

        layer = layers.color_continuous_layer(
            self.source,
            'name',
            widget=True
        )

        assert layer.widgets._widgets[0]._type == 'histogram'
        assert layer.widgets._widgets[0]._title == 'Distribution'

    def test_color_continuous_layer_animate(self, mocker):
        "should animate a property and disable the popups"
        setup_mocks(mocker)
        layer = layers.color_continuous_layer(
            self.source,
            'name',
            animate='time'
        )

        assert len(layer.popups.elements) == 0
        assert layer.widgets._widgets[0]._type == 'time-series'
        assert layer.widgets._widgets[0]._title == 'Animation'
        assert layer.widgets._widgets[0]._value == 'time'
