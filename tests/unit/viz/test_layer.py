from cartoframes.auth import Credentials
from cartoframes.viz.legend_list import LegendList
from cartoframes.viz.widget_list import WidgetList
from cartoframes.viz.popup_list import PopupList
from cartoframes.viz.source import Source
from cartoframes.viz.style import Style
from cartoframes.viz import Layer
from cartoframes.io.managers.context_manager import ContextManager


def setup_mocks(mocker, table_name):
    query = 'SELECT * FROM "public"."{}"'.format(table_name)
    mocker.patch.object(ContextManager, 'compute_query', return_value=query)
    mocker.patch.object(ContextManager, 'get_geom_type', return_value='point')
    mocker.patch.object(ContextManager, 'get_bounds')


class TestLayer(object):
    def test_is_layer_defined(self):
        """Layer"""
        assert Layer is not None

    def test_initialization_objects(self, mocker):
        """Layer should initialize layer attributes"""
        setup_mocks(mocker, 'layer_source')
        layer = Layer(Source('layer_source', credentials=Credentials('fakeuser')))

        assert layer.is_basemap is False
        assert layer.source_data == 'SELECT * FROM "public"."layer_source"'
        assert isinstance(layer.source, Source)
        assert isinstance(layer.style, Style)
        assert isinstance(layer.popups, PopupList)
        assert isinstance(layer.legends, LegendList)
        assert isinstance(layer.widgets, WidgetList)
        assert layer.interactivity == []

    def test_initialization_simple(self, mocker):
        """Layer should initialize layer attributes"""
        setup_mocks(mocker, 'layer_source')
        layer = Layer('layer_source', {}, credentials=Credentials('fakeuser'))

        assert layer.is_basemap is False
        assert layer.source_data == 'SELECT * FROM "public"."layer_source"'
        assert isinstance(layer.source, Source)
        assert isinstance(layer.style, Style)
        assert isinstance(layer.popups, PopupList)
        assert isinstance(layer.legends, LegendList)
        assert isinstance(layer.widgets, WidgetList)
        assert layer.interactivity == []
