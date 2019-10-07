from .context_mock import ContextMock
from .dataset_mock import DatasetMock
from .kuviz_mock import CartoKuvizMock


def mock_create_context(mocker, response=''):
    context_mock = ContextMock(response)
    mocker.spy(context_mock, 'execute_query')
    mocker.patch(
        'cartoframes.lib.context.create_context',
        return_value=context_mock)
    return context_mock


def mock_dataset(mocker, source, credentials=None):
    mock_create_context(mocker)
    return DatasetMock(source, credentials=credentials)


def mock_kuviz(name, html, credentials=None, password=None):
    return CartoKuvizMock(name=name, password=password)
