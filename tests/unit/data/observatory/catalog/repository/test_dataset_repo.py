import pytest

from cartoframes.auth import Credentials

from cartoframes.exceptions import DiscoveryException
from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.dataset import Dataset
from cartoframes.data.observatory.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.catalog.repository.repo_client import RepoClient
from ..examples import test_dataset1, test_datasets, db_dataset1, db_dataset2

try:
    from unittest.mock import patch, call
except ImportError:
    from mock import patch, call


class TestDatasetRepo(object):

    @patch.object(RepoClient, 'get_datasets')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        repo = DatasetRepository()

        # When
        datasets = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(RepoClient, 'get_datasets')
    @patch.object(RepoClient, 'set_user_credentials')
    def test_get_all_credentials(self, mocked_set_user_credentials, mocked_get_datasets):
        # Given
        mocked_get_datasets.return_value = [db_dataset1, db_dataset2]
        credentials = Credentials('user', '1234')
        repo = DatasetRepository()

        # When
        datasets = repo.get_all(credentials=credentials)

        # Then
        mocked_set_user_credentials.assert_has_calls([call(credentials), call(None)])
        mocked_get_datasets.assert_called_once_with(None)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(RepoClient, 'get_datasets')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        repo = DatasetRepository()

        # When
        datasets = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert datasets is None

    @patch.object(RepoClient, 'get_datasets')
    def test_get_all_only_uses_allowed_filters(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        repo = DatasetRepository()
        filters = {
            'country_id': 'usa',
            'category_id': 'demographics',
            'variable_id': 'population',
            'geography_id': 'census-geo',
            'variable_group_id': 'var-group',
            'provider_id': 'open_data',
            'fake_field_id': 'fake_value'
        }

        # When
        datasets = repo.get_all(filters)

        # Then
        mocked_repo.assert_called_once_with({
            'country_id': 'usa',
            'category_id': 'demographics',
            'variable_id': 'population',
            'geography_id': 'census-geo',
            'provider_id': 'open_data'
        })
        assert datasets == test_datasets

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1]
        requested_id = db_dataset1['id']
        repo = DatasetRepository()

        # When
        dataset = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with({'id': requested_id})
        assert dataset == test_dataset1

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = DatasetRepository()

        # Then
        with pytest.raises(DiscoveryException):
            repo.get_by_id(requested_id)

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_slug(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1]
        requested_slug = db_dataset1['slug']
        repo = DatasetRepository()

        # When
        dataset = repo.get_by_id(requested_slug)

        # Then
        mocked_repo.assert_called_once_with({'slug': requested_slug})
        assert dataset == test_dataset1

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_id_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        repo = DatasetRepository()

        # When
        datasets = repo.get_by_id_list([db_dataset1['id'], db_dataset2['id']])

        # Then
        mocked_repo.assert_called_once_with({'id': [db_dataset1['id'], db_dataset2['id']]})
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_slug_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        repo = DatasetRepository()

        # When
        datasets = repo.get_by_id_list([db_dataset1['slug'], db_dataset2['slug']])

        # Then
        mocked_repo.assert_called_once_with({'slug': [db_dataset1['slug'], db_dataset2['slug']]})
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_slug_and_id_list(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        repo = DatasetRepository()

        # When
        datasets = repo.get_by_id_list([db_dataset1['id'], db_dataset2['slug']])

        # Then
        mocked_repo.assert_called_once_with({'id': [db_dataset1['id']], 'slug': [db_dataset2['slug']]})
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(RepoClient, 'get_datasets')
    def test_missing_fields_are_mapped_as_None(self, mocked_repo):
        # Given
        mocked_repo.return_value = [{'id': 'dataset1'}]
        repo = DatasetRepository()

        expected_datasets = CatalogList([Dataset({
            'id': 'dataset1',
            'slug': None,
            'name': None,
            'description': None,
            'provider_id': None,
            'provider_name': None,
            'category_id': None,
            'category_name': None,
            'data_source_id': None,
            'country_id': None,
            'lang': None,
            'geography_id': None,
            'geography_name': None,
            'geography_description': None,
            'temporal_aggregation': None,
            'time_coverage': None,
            'update_frequency': None,
            'version': None,
            'is_public_data': None,
            'summary_json': None,
            'available_in': None
        })])

        # When
        datasets = repo.get_all()

        # Then
        assert datasets == expected_datasets
