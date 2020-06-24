import pytest

from cartoframes.auth import Credentials
from cartoframes.viz import Layer, Layout, Map
from cartoframes.viz.source import Source

from cartoframes.io.managers.context_manager import ContextManager

from .utils import build_geodataframe

from ..mocks.kuviz_mock import KuvizPublisherMock


def setup_mocks(mocker):
    mocker.patch('cartoframes.viz.layout._get_publisher', return_value=KuvizPublisherMock())
    mocker.patch.object(ContextManager, 'compute_query', return_value='select * from fake_table')
    mocker.patch.object(ContextManager, 'get_geom_type', return_value='point')
    mocker.patch.object(ContextManager, 'get_bounds', return_value=None)


SOURCE = build_geodataframe([-10, 0], [-10, 0])


class TestLayout(object):
    def test_is_defined(self):
        """Layout"""
        assert Layout is not None


class TestLayoutInitialization(object):
    def test__init(self):
        """Layout should init properly"""
        layout = Layout([])
        assert layout._layout is not None
        assert layout._n_size == 0
        assert layout._m_size == 1
        assert layout._viewport is None
        assert layout._is_static is False

    def test__init_maps(self):
        """Layout should init properly"""
        layout = Layout([Map(Layer(Source(SOURCE))),
                         Map(Layer(Source(SOURCE)))])
        assert layout._n_size == 2
        assert layout._m_size == 1

    def test__init_maps_valid(self):
        """Layout should raise an error if any element in the map list is not a Map"""

        msg = 'All the elements in the Layout should be an instance of Map.'
        with pytest.raises(Exception) as e:
            Layout([Layer(Source(SOURCE))])
        assert str(e.value) == msg

    def test__init_maps_size(self):
        """Layout should init properly"""
        layout = Layout([Map(Layer(Source(SOURCE))),
                         Map(Layer(Source(SOURCE)))], 1, 2)
        assert layout._n_size == 1
        assert layout._m_size == 2


class TestLayoutSettings(object):
    def test_global_viewport(self):
        """Layout should return the same viewport for every map"""
        layout = Layout([
            Map(Layer(Source(SOURCE))),
            Map(Layer(Source(SOURCE)))
        ], viewport={'zoom': 5})

        assert layout._layout[0].get('viewport') == {'zoom': 5}
        assert layout._layout[1].get('viewport') == {'zoom': 5}

    def test_custom_viewport(self):
        """Layout should return a different viewport for every map"""
        layout = Layout([
            Map(Layer(Source(SOURCE)), viewport={'zoom': 2}),
            Map(Layer(Source(SOURCE)))
        ], viewport={'zoom': 5})

        assert layout._layout[0].get('viewport') == {'zoom': 2}
        assert layout._layout[1].get('viewport') == {'zoom': 5}

    def test_global_camera(self):
        """Layout should return the correct camera for each map"""
        layout = Layout([
            Map(Layer(Source(SOURCE))),
            Map(Layer(Source(SOURCE)))
        ], viewport={'zoom': 5})

        assert layout._layout[0].get('camera') == {
            'bearing': None, 'center': None, 'pitch': None, 'zoom': 5}
        assert layout._layout[1].get('camera') == {
            'bearing': None, 'center': None, 'pitch': None, 'zoom': 5}

    def test_custom_camera(self):
        """Layout should return the correct camera for each map"""
        layout = Layout([
            Map(Layer(Source(SOURCE)), viewport={'zoom': 2}),
            Map(Layer(Source(SOURCE)))
        ], viewport={'zoom': 5})

        assert layout._layout[0].get('camera') == {
            'bearing': None, 'center': None, 'pitch': None, 'zoom': 2}
        assert layout._layout[1].get('camera') == {
            'bearing': None, 'center': None, 'pitch': None, 'zoom': 5}

    def test_is_static(self):
        """Layout should set correctly is_static property for each map"""
        layout = Layout([
            Map(Layer(Source(SOURCE))),
            Map(Layer(Source(SOURCE)))
        ], is_static=True)

        assert layout._layout[0].get('is_static') is True
        assert layout._layout[1].get('is_static') is True


class TestLayoutPublication:
    def setup_method(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.credentials = Credentials(username=self.username, api_key=self.api_key)
        self.test_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            -3.1640625,
                            42.032974332441405
                        ]
                    }
                }
            ]
        }

    def assert_kuviz_dict(self, kuviz_dict, name, privacy):
        assert kuviz_dict['id'] is not None
        assert kuviz_dict['url'] is not None
        assert kuviz_dict['name'] == name
        assert kuviz_dict['privacy'] == privacy

    def test_layout_publish_remote_default(self, mocker):
        setup_mocks(mocker)
        mock_set_content = mocker.patch('cartoframes.viz.html.html_layout.HTMLLayout.set_content')

        vlayout = Layout([Map(Layer('fake_table', credentials=self.credentials))])

        name = 'cf_publish'
        kuviz_dict = vlayout.publish(name, None, self.credentials)
        self.assert_kuviz_dict(kuviz_dict, name, 'public')
        mock_set_content.assert_called_once_with(
            is_embed=True,
            is_static=False,
            m_size=1,
            n_size=1,
            size=['100%', 250],
            map_height='100%',
            maps=[{
                'layers': [{
                    'credentials': {
                        'username': 'fake_username',
                        'api_key': 'fake_api_key',
                        'base_url': 'https://fake_username.carto.com'
                    },
                    'interactivity': [],
                    'legends': [],
                    'has_legend_list': True,
                    'encode_data': True,
                    'widgets': [],
                    'data': 'select * from fake_table',
                    'type': 'Query',
                    'title': None,
                    'options': {},
                    'map_index': 0,
                    'source': 'select * from fake_table',
                    'viz': '''color: hex("#EE4D5A")
strokeColor: opacity(#222,ramp(linear(zoom(),0,18),[0,0.6]))
strokeWidth: ramp(linear(zoom(),0,18),[0,1])
width: ramp(linear(zoom(),0,18),[2,10])
'''
                }],
                'bounds': [[-180, -90], [180, 90]],
                'size': None,
                'viewport': None,
                'camera': None,
                'basemap': 'Positron',
                'basecolor': '',
                'token': '',
                'show_info': None,
                'has_legends': False,
                'has_widgets': False,
                'theme': None,
                'title': None,
                'description': None,
                'is_static': False,
                'layer_selector': False,
                '_carto_vl_path': None,
                '_airship_path': None
            }]
        )

    def test_layout_publish_remote_params(self, mocker):
        setup_mocks(mocker)
        mock_set_content = mocker.patch('cartoframes.viz.html.html_layout.HTMLLayout.set_content')

        vlayout = Layout([Map(
            Layer('fake_table', credentials=self.credentials),
            basemap='yellow',
            bounds={'west': 1, 'east': 2, 'north': 3, 'south': 4},
            viewport={'zoom': 5, 'lat': 50, 'lng': -10},
            is_static=True,
            layer_selector=False,
            theme='dark',
            title='title',
            description='description'
        )])

        name = 'cf_publish'
        kuviz_dict = vlayout.publish(name, None, self.credentials, maps_api_key='1234567890')
        self.assert_kuviz_dict(kuviz_dict, name, 'public')
        mock_set_content.assert_called_once_with(
            is_embed=True,
            is_static=False,
            m_size=1,
            n_size=1,
            size=['100%', 250],
            map_height='100%',
            maps=[{
                'layers': [{
                    'credentials': {
                        'username': 'fake_username',
                        'api_key': '1234567890',
                        'base_url': 'https://fake_username.carto.com'
                    },
                    'interactivity': [],
                    'legends': [],
                    'has_legend_list': True,
                    'encode_data': True,
                    'widgets': [],
                    'data': 'select * from fake_table',
                    'type': 'Query',
                    'title': None,
                    'options': {},
                    'map_index': 0,
                    'source': 'select * from fake_table',
                    'viz': '''color: hex("#EE4D5A")
strokeColor: opacity(#222,ramp(linear(zoom(),0,18),[0,0.6]))
strokeWidth: ramp(linear(zoom(),0,18),[0,1])
width: ramp(linear(zoom(),0,18),[2,10])
'''
                }],
                'bounds': [[1, 2], [4, 3]],
                'size': None,
                'viewport': {'zoom': 5, 'lat': 50, 'lng': -10},
                'camera': {'center': [-10, 50], 'zoom': 5, 'bearing': None, 'pitch': None},
                'basemap': 'yellow',
                'basecolor': 'yellow',
                'token': '',
                'show_info': None,
                'has_legends': False,
                'has_widgets': False,
                'theme': 'dark',
                'title': 'title',
                'description': 'description',
                'is_static': True,
                'layer_selector': False,
                '_carto_vl_path': None,
                '_airship_path': None
            }]
        )
