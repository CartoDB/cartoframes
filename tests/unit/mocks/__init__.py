from .kuviz_mock import CartoKuvizMock


def mock_kuviz(name, html, credentials=None, password=None):
    return CartoKuvizMock(name=name, password=password)
