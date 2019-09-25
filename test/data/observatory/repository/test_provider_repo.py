import unittest

from cartoframes.exceptions import DiscoveryException

from cartoframes.data.observatory.repository.provider_repo import ProviderRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_provider1, test_providers, db_provider1, db_provider2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestProviderRepo(unittest.TestCase):

    @patch.object(RepoClient, 'get_providers')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_provider1, db_provider2]
        repo = ProviderRepository()

        # When
        providers = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with()
        assert providers == test_providers

    @patch.object(RepoClient, 'get_providers')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        repo = ProviderRepository()

        # When
        providers = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with()
        assert providers is None

    @patch.object(RepoClient, 'get_providers')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_provider1, db_provider2]
        requested_id = test_provider1['id']
        repo = ProviderRepository()

        # When
        provider = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with('id', requested_id)
        assert provider == test_provider1

    @patch.object(RepoClient, 'get_providers')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = ProviderRepository()

        # Then
        with self.assertRaises(DiscoveryException):
            repo.get_by_id(requested_id)
