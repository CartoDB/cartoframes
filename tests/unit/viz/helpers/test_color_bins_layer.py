import pytest

from cartoframes.viz import helpers
from cartoframes.auth import Credentials

from . import setup_mocks
from ..utils import build_cartodataframe


class TestColorBinsLayerHelper(object):
    def setup_method(self):
        self.source = build_cartodataframe([0], [0], ['name', 'time'])

    def test_helpers(self):
        "should be defined"
        assert helpers.color_bins_layer is not None

    def test_color_bins_layer(self, mocker):
        "should create a layer with the proper attributes"
        setup_mocks(mocker)
        layer = helpers.color_bins_layer(
            source='SELECT * FROM faketable',
            value='name',
            credentials=Credentials('fakeuser')
        )

        assert layer.style is not None
        assert layer.style._style['point']['color'] == 'opacity(ramp(globalQuantiles($name, 5), purpor),1)'
        assert layer.style._style['line']['color'] == 'opacity(ramp(globalQuantiles($name, 5), purpor),1)'
        assert layer.style._style['polygon']['color'] == 'opacity(ramp(globalQuantiles($name, 5), purpor), 0.9)'
        assert layer.popup is not None
        assert layer.popup._hover == [{
            'title': 'name',
            'value': '$name'
        }]

        assert layer.legend is not None
        assert layer.legend._type['point'] == 'color-bins-point'
        assert layer.legend._type['line'] == 'color-bins-line'
        assert layer.legend._type['polygon'] == 'color-bins-polygon'
        assert layer.legend._title == 'name'
        assert layer.legend._description == ''
        assert layer.legend._footer == ''

    def test_color_bins_layer_point(self, mocker):
        "should create a point type layer"
        setup_mocks(mocker)
        layer = helpers.color_bins_layer(
            self.source,
            'name',
            'Neighborhoods',
            bins=3,
            palette='prism'
        )

        assert layer.style._style['point']['color'] == 'opacity(ramp(globalQuantiles($name, 3), prism),1)'

    def test_color_bins_layer_line(self, mocker):
        "should create a line type layer"
        setup_mocks(mocker, 'line')
        layer = helpers.color_bins_layer(
            self.source,
            'name',
            'Neighborhoods',
            bins=3,
            palette='[blue,#F00]'
        )

        assert layer.style._style['line']['color'] == 'opacity(ramp(globalQuantiles($name, 3), [blue,#F00]),1)'

    def test_color_bins_layer_polygon(self, mocker):
        "should create a polygon type layer"
        setup_mocks(mocker, 'polygon')
        layer = helpers.color_bins_layer(
            self.source,
            'name',
            'Neighborhoods',
            bins=3,
            palette=['blue', '#F00']
        )

        assert layer.style._style['polygon']['color'] == 'opacity(ramp(globalQuantiles($name, 3), [blue,#F00]), 0.9)'

    def test_color_bins_layer_method(self, mocker):
        "should apply the classification method"
        setup_mocks(mocker)
        layer = helpers.color_bins_layer(
            self.source,
            'name',
            method='quantiles'
        )

        assert layer.style._style['point']['color'] == 'opacity(ramp(globalQuantiles($name, 5), purpor),1)'
        assert layer.style._style['line']['color'] == 'opacity(ramp(globalQuantiles($name, 5), purpor),1)'
        assert layer.style._style['polygon']['color'] == 'opacity(ramp(globalQuantiles($name, 5), purpor), 0.9)'

        layer = helpers.color_bins_layer(
            self.source,
            'name',
            method='equal'
        )

        assert layer.style._style['point']['color'] == 'opacity(ramp(globalEqIntervals($name, 5), purpor),1)'
        assert layer.style._style['line']['color'] == 'opacity(ramp(globalEqIntervals($name, 5), purpor),1)'
        assert layer.style._style['polygon']['color'] == 'opacity(ramp(globalEqIntervals($name, 5), purpor), 0.9)'

        layer = helpers.color_bins_layer(
            self.source,
            'name',
            method='stdev'
        )

        assert layer.style._style['point']['color'] == 'opacity(ramp(globalStandardDev($name, 5), temps),1)'
        assert layer.style._style['line']['color'] == 'opacity(ramp(globalStandardDev($name, 5), temps),1)'
        assert layer.style._style['polygon']['color'] == 'opacity(ramp(globalStandardDev($name, 5), temps), 0.9)'

        msg = 'Available methods are: "quantiles", "equal", "stdev".'
        with pytest.raises(ValueError) as e:
            helpers.color_bins_layer(
                self.source,
                'name',
                method='wrong_method'
            )
        assert str(e.value) == msg

    def test_color_bins_layer_breaks(self, mocker):
        "should apply buckets if breaks are passed"
        setup_mocks(mocker)
        layer = helpers.color_bins_layer(
            self.source,
            'name',
            breaks=[0, 1, 2]
        )

        assert layer.style._style['point']['color'] == 'opacity(ramp(buckets($name, [0, 1, 2]), purpor),1)'
        assert layer.style._style['line']['color'] == 'opacity(ramp(buckets($name, [0, 1, 2]), purpor),1)'
        assert layer.style._style['polygon']['color'] == 'opacity(ramp(buckets($name, [0, 1, 2]), purpor), 0.9)'

    def test_color_bins_layer_legend(self, mocker):
        "should show/hide the legend"
        setup_mocks(mocker)
        layer = helpers.color_bins_layer(
            self.source,
            'name',
            legend=False
        )

        assert layer.legend._type == ''
        assert layer.legend._title == ''

        layer = helpers.color_bins_layer(
            self.source,
            'name',
            legend=True
        )

        assert layer.legend._type == {
            'point': 'color-bins-point',
            'line': 'color-bins-line',
            'polygon': 'color-bins-polygon'
        }
        assert layer.legend._title == 'name'

    def test_color_bins_layer_popup(self, mocker):
        "should show/hide the popup"
        setup_mocks(mocker)
        layer = helpers.color_bins_layer(
            self.source,
            'name',
            popup=False
        )

        assert layer.popup._hover == []

        layer = helpers.color_bins_layer(
            self.source,
            'name',
            popup=True
        )

        assert layer.popup._hover == [{
            'title': 'name',
            'value': '$name'
        }]

    def test_color_bins_layer_widget(self, mocker):
        "should show/hide the widget"
        setup_mocks(mocker)
        layer = helpers.color_bins_layer(
            self.source,
            'name',
            widget=False
        )

        assert layer.widgets._widgets == []

        layer = helpers.color_bins_layer(
            self.source,
            'name',
            widget=True
        )

        assert layer.widgets._widgets[0]._type == 'histogram'
        assert layer.widgets._widgets[0]._title == 'Distribution'

    def test_color_bins_layer_animate(self, mocker):
        "should animate a property and disable the popups"
        setup_mocks(mocker)
        layer = helpers.color_bins_layer(
            self.source,
            'name',
            animate='time'
        )

        assert layer.popup._hover == []
        assert layer.widgets._widgets[0]._type == 'time-series'
        assert layer.widgets._widgets[0]._title == 'Animation'
        assert layer.widgets._widgets[0]._value == 'time'
