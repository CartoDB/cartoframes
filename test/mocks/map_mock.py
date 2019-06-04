from cartoframes.viz import Map

from mocks.kuviz_mock import KuvizPublisherMock

class MapMock(Map):
    def _get_publisher(self):
        return KuvizPublisherMock(self)
