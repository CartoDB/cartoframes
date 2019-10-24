from cartoframes.viz import Map

from ..mocks.kuviz_mock import KuvizPublisherMock


class MapMock(Map):
    def _get_publisher(self):
        return KuvizPublisherMock(self.layers)

    def _get_publication_html(self, name, maps_api_key):
        return "<html><body><h1>Hi Kuviz yeee</h1></body></html>"
