from cartoframes.auth import Credentials
from cartoframes.viz import Map, Layer, popup_element, constants
from cartoframes.viz.source import Source

from cartoframes.viz.kuviz import KuvizPublisher, kuviz_to_dict
from cartoframes.io.managers.context_manager import ContextManager

from .utils import build_geodataframe

from ..mocks.kuviz_mock import CartoKuvizMock


def setup_mocks(mocker):
    mocker.patch('cartoframes.viz.map._get_publisher', return_value=KuvizPublisherMock())
    mocker.patch.object(ContextManager, 'compute_query')
    mocker.patch.object(ContextManager, 'get_geom_type', return_value='point')
    mocker.patch.object(ContextManager, 'get_bounds', return_value=None)


class TestMap(object):
    def test_is_defined(self):
        """Map"""
        assert Map is not None


class TestMapInitialization(object):
    def test_size(self):
        """Map should set the size by default"""
        map = Map()
        assert map.size is None

    def test__init(self):
        """Map should return a valid template"""
        map = Map()
        map._repr_html_()
        assert map.bounds is not None
        assert map._html_map is not None

    def test_bounds(self):
        """Map should set the bounds"""
        map = Map(bounds={
            'west': -10,
            'east': 10,
            'north': -10,
            'south': 10
        })
        assert map.bounds == [[-10, 10], [10, -10]]

    def test_bounds_clamp(self):
        """Map should set the bounds clamped"""
        map = Map(bounds={
            'west': -1000,
            'east': 1000,
            'north': -1000,
            'south': 1000
        })
        assert map.bounds == [[-180, 90], [180, -90]]


class TestMapLayer(object):
    def test_one_layer(self):
        """Map layer should be able to initialize one layer"""
        source = Source(build_geodataframe([-10, 0], [-10, 0]))
        layer = Layer(source)
        map = Map(layer)

        assert map.layers == [layer]
        assert len(map.layer_defs) == 1
        assert map.layer_defs[0].get('interactivity') == []
        assert map.layer_defs[0].get('credentials') is None
        assert map.layer_defs[0].get('legends') is not None
        assert map.layer_defs[0].get('widgets') is not None
        assert map.layer_defs[0].get('data') is not None
        assert map.layer_defs[0].get('type') == 'GeoJSON'
        assert map.layer_defs[0].get('viz') is not None

    def test_two_layers(self):
        """Map layer should be able to initialize two layers in the correct order"""
        source_1 = Source(build_geodataframe([-10, 0], [-10, 0]))
        source_2 = Source(build_geodataframe([0, 10], [10, 0]))
        layer_1 = Layer(source_1)
        layer_2 = Layer(source_2)
        map = Map([layer_1, layer_2])

        assert map.layers == [layer_1, layer_2]
        assert len(map.layer_defs) == 2

    def test_interactive_layer(self):
        """Map layer should indicate if the layer has interactivity configured"""
        source_1 = Source(build_geodataframe([-10, 0], [-10, 0], ['pop', 'name']))
        layer = Layer(
            source_1,
            popup_click=[
                popup_element('pop'),
                popup_element('name')
            ],
            popup_hover=[
                popup_element('pop', 'Pop')
            ]
        )

        map = Map(layer)
        assert map.layer_defs[0].get('interactivity') == [
            {
                'event': 'click',
                'attrs': {
                    'name': 'v6ae999',
                    'title': 'name'
                }
            }, {
                'event': 'click',
                'attrs': {
                    'name': 'v4f197c',
                    'title': 'pop'
                }
            }, {
                'event': 'hover',
                'attrs': {
                    'name': 'v4f197c',
                    'title': 'Pop'
                }
            }
        ]

    def test_default_interactive_layer(self):
        """Map layer should get the default event if the interactivity is set to []"""
        source_1 = Source(build_geodataframe([-10, 0], [-10, 0]))
        layer = Layer(
            source_1
        )

        map = Map(layer)
        assert map.layer_defs[0].get('interactivity') == []


class TestMapDevelopmentPath(object):
    def test_default_carto_vl_path(self):
        """Map dev path should use default paths if none are given"""
        map = Map()
        map._repr_html_()
        template = map._html_map.html
        assert constants.CARTO_VL_URL in template

    def test_custom_carto_vl_path(self):
        """Map dev path should use custom paths"""
        _carto_vl_path = 'custom_carto_vl_path'
        map = Map(_carto_vl_path=_carto_vl_path)
        map._repr_html_()
        template = map._html_map.html
        assert _carto_vl_path + constants.CARTO_VL_DEV in template

    def test_default_airship_path(self):
        """Map dev path should use default paths if none are given"""
        map = Map()
        map._repr_html_()
        template = map._html_map.html
        assert constants.AIRSHIP_COMPONENTS_URL in template
        assert constants.AIRSHIP_BRIDGE_URL in template
        assert constants.AIRSHIP_STYLES_URL in template
        assert constants.AIRSHIP_MODULE_URL in template
        assert constants.AIRSHIP_ICONS_URL in template

    def test_custom_airship_path(self):
        """Map dev path should use custom paths"""
        _airship_path = 'custom_airship_path'
        map = Map(_airship_path=_airship_path)
        map._repr_html_()
        template = map._html_map.html
        assert _airship_path + constants.AIRSHIP_COMPONENTS_DEV in template
        assert _airship_path + constants.AIRSHIP_BRIDGE_DEV in template
        assert _airship_path + constants.AIRSHIP_STYLES_DEV in template
        assert _airship_path + constants.AIRSHIP_MODULE_DEV in template
        assert _airship_path + constants.AIRSHIP_ICONS_DEV in template


class KuvizPublisherMock(KuvizPublisher):
    def __init__(self):
        pass

    def get_layers(self):
        return []

    def set_layers(self, layers, map_api_key):
        pass

    def publish(self, html, name, password, if_exists='fail'):
        self.kuviz = CartoKuvizMock(name, password=password)
        return kuviz_to_dict(self.kuviz)


class TestMapPublication(object):
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

    def test_map_publish_remote_default(self, mocker):
        setup_mocks(mocker)
        mock_set_content = mocker.patch('cartoframes.viz.html.html_map.HTMLMap.set_content')

        vmap = Map(Layer('fake_table', credentials=self.credentials))

        name = 'cf_publish'
        kuviz_dict = vmap.publish(name, None, self.credentials)
        self.assert_kuviz_dict(kuviz_dict, name, 'public')
        mock_set_content.assert_called_once_with(
            _airship_path=None,
            _carto_vl_path=None,
            basemap='Positron',
            bounds=[[-180, -90], [180, 90]],
            camera=None,
            description=None,
            is_embed=True,
            is_static=None,
            layer_selector=False,
            layers=[],
            show_info=False,
            size=None,
            theme=None,
            title='cf_publish'
        )

    def test_map_publish_remote_params(self, mocker):
        setup_mocks(mocker)
        mock_set_content = mocker.patch('cartoframes.viz.html.html_map.HTMLMap.set_content')

        vmap = Map(
            Layer('fake_table', credentials=self.credentials),
            basemap='yellow',
            bounds={'west': 1, 'east': 2, 'north': 3, 'south': 4},
            viewport={'zoom': 5, 'lat': 50, 'lng': -10},
            is_static=True,
            layer_selector=False,
            theme='dark',
            title='title',
            description='description'
        )

        name = 'cf_publish'
        kuviz_dict = vmap.publish(name, None, self.credentials)
        self.assert_kuviz_dict(kuviz_dict, name, 'public')
        mock_set_content.assert_called_once_with(
            _airship_path=None,
            _carto_vl_path=None,
            basemap='yellow',
            bounds=[[1, 2], [4, 3]],
            camera={'bearing': None, 'center': [-10, 50], 'pitch': None, 'zoom': 5},
            description='description',
            is_embed=True,
            is_static=True,
            layer_selector=False,
            layers=[],
            show_info=False,
            size=None,
            theme='dark',
            title='cf_publish'
        )

    def test_map_publish_with_password(self, mocker):
        setup_mocks(mocker)

        map = Map(Layer(Source('fake_table', credentials=self.credentials)))

        name = 'cf_publish'
        kuviz_dict = map.publish(name, '1234', credentials=self.credentials)
        self.assert_kuviz_dict(kuviz_dict, name, 'password')

    def test_map_publish_deletion(self, mocker):
        setup_mocks(mocker)

        map = Map(Layer(Source('fake_table', credentials=self.credentials)))

        name = 'cf_publish'
        map.publish(name, None, credentials=self.credentials)
        response = map.delete_publication()

        assert response is True

    def test_map_publish_update_name(self, mocker):
        setup_mocks(mocker)

        map = Map(Layer(Source('fake_table', credentials=self.credentials)))

        name = 'cf_publish'
        map.publish(name, None, credentials=self.credentials)

        new_name = 'cf_update'
        kuviz_dict = map.update_publication(new_name, password=None)

        self.assert_kuviz_dict(kuviz_dict, new_name, 'public')

    def test_map_publish_update_password(self, mocker):
        setup_mocks(mocker)

        map = Map(Layer(Source('fake_table', credentials=self.credentials)))

        name = 'cf_publish'
        map.publish(name, None, credentials=self.credentials)
        kuviz_dict = map.update_publication(name, '1234"')

        self.assert_kuviz_dict(kuviz_dict, name, 'password')
