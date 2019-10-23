from cartoframes.viz import helpers

from . import setup_mocks


class TestColorContinuousLayerHelper(object):
    def test_helpers(self):
        "should be defined"
        assert helpers.color_continuous_layer is not None

    def test_color_continuous_layer(self, mocker):
        "should create a layer with the proper attributes"
        setup_mocks(mocker)
        layer = helpers.color_continuous_layer(
            source='sf_neighborhoods',
            value='name'
        )

        assert layer.style is not None
        assert layer.style._style['point']['color'] == 'opacity(ramp(linear($name), bluyl),1)'
        assert layer.style._style['line']['color'] == 'opacity(ramp(linear($name), bluyl),1)'
        assert layer.style._style['polygon']['color'] == 'opacity(ramp(linear($name), bluyl), 0.9)'
        assert layer.popup, None
        assert layer.popup._hover == [{
            'title': 'name',
            'value': '$name'
        }]

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
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            palette='prism'
        )

        assert layer.style._style['point']['color'] == 'opacity(ramp(linear($name), prism),1)'

    def test_color_continuous_layer_line(self, mocker):
        "should create a line type layer"
        setup_mocks(mocker, 'line')
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            palette='[blue,#F00]'
        )

        assert layer.style._style['line']['color'] == 'opacity(ramp(linear($name), [blue,#F00]),1)'

    def test_color_continuous_layer_polygon(self, mocker):
        "should create a polygon type layer"
        setup_mocks(mocker, 'polygon')
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            'Neighborhoods',
            palette=['blue', '#F00']
        )

        assert layer.style._style['polygon']['color'] == 'opacity(ramp(linear($name), [blue,#F00]), 0.9)'

    def test_color_continuous_layer_legend(self, mocker):
        "should show/hide the legend"
        setup_mocks(mocker)
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            legend=False
        )

        assert layer.legend._type == ''
        assert layer.legend._title == ''

        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
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
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            popup=False
        )

        assert layer.popup._hover == []

        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            popup=True
        )

        assert layer.popup._hover == [{
            'title': 'name',
            'value': '$name'
        }]

    def test_color_continuous_layer_widget(self, mocker):
        "should show/hide the widget"
        setup_mocks(mocker)
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            widget=False
        )

        assert layer.widgets._widgets == []

        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            widget=True
        )

        assert layer.widgets._widgets[0]._type == 'histogram'
        assert layer.widgets._widgets[0]._title == 'Distribution'

    def test_color_continuous_layer_animate(self, mocker):
        "should animate a property and disable the popups"
        setup_mocks(mocker)
        layer = helpers.color_continuous_layer(
            'sf_neighborhoods',
            'name',
            animate='time'
        )

        assert layer.popup._hover == []
        assert layer.widgets._widgets[0]._type == 'time-series'
        assert layer.widgets._widgets[0]._title == 'Animation'
        assert layer.widgets._widgets[0]._value == 'time'
