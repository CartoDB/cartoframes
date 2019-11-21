import pytest

from cartoframes.viz import Source
from cartoframes.auth import Credentials
from cartoframes.core.managers.context_manager import ContextManager


def setup_mocks(mocker):
    mocker.patch.object(ContextManager, 'compute_query')


class TestSource(object):
    def test_is_source_defined(self):
        """Source"""
        assert Source is not None

    def test_source_get_credentials_username(self, mocker):
        """Source should return the correct credentials when username is provided"""
        setup_mocks(mocker)
        source = Source('faketable', credentials=Credentials(
            username='fakeuser', api_key='1234'))

        credentials = source.get_credentials()

        assert credentials['username'] == 'fakeuser'
        assert credentials['api_key'] == '1234'
        assert credentials['base_url'] == 'https://fakeuser.carto.com'

    def test_source_get_credentials_base_url(self, mocker):
        """Source should return the correct credentials when base_url is provided"""
        setup_mocks(mocker)
        source = Source('faketable', credentials=Credentials(
            base_url='https://fakeuser.carto.com'))

        credentials = source.get_credentials()

        assert credentials['username'] == 'user'
        assert credentials['api_key'] == 'default_public'
        assert credentials['base_url'] == 'https://fakeuser.carto.com'

    def test_source_no_credentials(self):
        """Source should raise an exception if there are no credentials"""
        with pytest.raises(AttributeError) as e:
            Source('faketable')

        assert str(e.value) == ('Credentials attribute is required. '
                                'Please pass a `Credentials` instance or use '
                                'the `set_default_credentials` function.')
