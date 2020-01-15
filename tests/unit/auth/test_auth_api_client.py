from cartoframes.viz.source import Source
from cartoframes.auth import Credentials
from cartoframes.data.clients.auth_api_client import AuthAPIClient
from cartoframes.io.managers.context_manager import ContextManager

from ..mocks.api_key_mock import APIKeyManagerMock

TOKEN_MOCK = '1234'


def setup_mocks(mocker):
    mocker.patch(
        'cartoframes.data.clients.auth_api_client._get_api_key_manager',
        return_value=APIKeyManagerMock(TOKEN_MOCK))
    mocker.patch.object(ContextManager, 'compute_query')
    mocker.patch.object(ContextManager, 'get_schema')
    mocker.patch.object(ContextManager, 'get_table_names')


class TestAuthAPIClient(object):
    def test_instantiation(self, mocker):
        setup_mocks(mocker)

        auth_api_client = AuthAPIClient()

        assert isinstance(auth_api_client, AuthAPIClient)
        assert isinstance(auth_api_client._api_key_manager, APIKeyManagerMock)

    def test_create_api_key(self, mocker):
        setup_mocks(mocker)

        source = Source('fake_table', credentials=Credentials('fakeuser'))
        api_key_name = 'fake_name'

        auth_api_client = AuthAPIClient()
        token, tables = auth_api_client.create_api_key([source], name=api_key_name)

        assert token == TOKEN_MOCK

    def test_create_api_key_several_sources(self, mocker):
        setup_mocks(mocker)

        source = Source('fake_table', credentials=Credentials('fakeuser'))
        api_key_name = 'fake_name'

        auth_api_client = AuthAPIClient()
        token, tables = auth_api_client.create_api_key([source, source, source], name=api_key_name)

        assert token == TOKEN_MOCK
