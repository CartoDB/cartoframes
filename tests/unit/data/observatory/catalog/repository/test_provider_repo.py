import pytest

from unittest.mock import patch

from cartoframes.exceptions import CatalogError
from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.provider import Provider
from cartoframes.data.observatory.catalog.repository.provider_repo import ProviderRepository
from cartoframes.data.observatory.catalog.repository.repo_client import RepoClient
from ..examples import test_provider1, test_providers, db_provider1, db_provider2


class TestProviderRepo(object):

    @patch.object(RepoClient, 'get_providers')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_provider1, db_provider2]
        repo = ProviderRepository()

        # When
        providers = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert isinstance(providers, CatalogList)
        assert providers == test_providers

    @patch.object(RepoClient, 'get_providers')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        repo = ProviderRepository()

        # When
        providers = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert providers is None

    @patch.object(RepoClient, 'get_providers')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_provider1, db_provider2]
        requested_id = db_provider1['id']
        repo = ProviderRepository()

        # When
        provider = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with({'id': [requested_id]})
        assert isinstance(provider, Provider)
        assert provider == test_provider1

    @patch.object(RepoClient, 'get_providers')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = ProviderRepository()

        # Then
        with pytest.raises(CatalogError):
            repo.get_by_id(requested_id)

    @patch.object(RepoClient, 'get_providers')
    def test_missing_fields_are_mapped_as_None(self, mocked_repo):
        # Given
        mocked_repo.return_value = [{'id': 'provider1'}]
        repo = ProviderRepository()

        expected_providers = CatalogList([Provider({
            'id': 'provider1',
            'name': None
        })])

        # When
        providers = repo.get_all()

        # Then
        assert providers == expected_providers
