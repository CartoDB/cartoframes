import unittest

from cartoframes.auth import Credentials
from cartoframes.data.observatory.dataset import Dataset

from cartoframes.exceptions import DiscoveryException
from cartoframes.data.observatory.entity import CatalogList
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_dataset1, test_datasets, db_dataset1, db_dataset2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestDatasetRepo(unittest.TestCase):

    @patch.object(RepoClient, 'get_datasets')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        repo = DatasetRepository()

        # When
        datasets = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None, None)
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
        datasets = repo.get_all(credentials)

        # Then
        mocked_set_user_credentials.assert_called_once_with(credentials)
        mocked_get_datasets.assert_called_once_with(None, None)
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
        mocked_repo.assert_called_once_with(None, None)
        assert datasets is None

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        requested_id = db_dataset1['id']
        repo = DatasetRepository()

        # When
        dataset = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with('id', requested_id)
        assert dataset == test_dataset1

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = DatasetRepository()

        # Then
        with self.assertRaises(DiscoveryException):
            repo.get_by_id(requested_id)

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        country_code = 'esp'
        repo = DatasetRepository()

        # When
        datasets = repo.get_by_country(country_code)

        # Then
        mocked_repo.assert_called_once_with('country_id', country_code)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_category(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        category_id = 'cat1'
        repo = DatasetRepository()

        # When
        datasets = repo.get_by_category(category_id)

        # Then
        mocked_repo.assert_called_once_with('category_id', category_id)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_variable(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        variable_id = 'var1'
        repo = DatasetRepository()

        # When
        datasets = repo.get_by_variable(variable_id)

        # Then
        mocked_repo.assert_called_once_with('variable_id', variable_id)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(RepoClient, 'get_datasets')
    def test_get_by_geography(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_dataset1, db_dataset2]
        geography_id = 'geo_id'
        repo = DatasetRepository()

        # When
        datasets = repo.get_by_geography(geography_id)

        # Then
        mocked_repo.assert_called_once_with('geography_id', geography_id)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(RepoClient, 'get_datasets')
    def test_missing_fields_are_mapped_as_None(self, mocked_repo):
        # Given
        mocked_repo.return_value = [{'id': 'dataset1'}]
        repo = DatasetRepository()

        expected_datasets = CatalogList([Dataset({
            'id': 'dataset1',
            'name': None,
            'description': None,
            'provider_id': None,
            'category_id': None,
            'data_source_id': None,
            'country_id': None,
            'lang': None,
            'geography_id': None,
            'temporal_aggregation': None,
            'time_coverage': None,
            'update_frequency': None,
            'version': None,
            'is_public_data': None,
            'summary_jsonb': None
        })])

        # When
        datasets = repo.get_all()

        # Then
        assert datasets == expected_datasets
