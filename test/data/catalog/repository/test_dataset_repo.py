import unittest
from cartoframes.data.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.catalog.repository.repo_client import RepoClient

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestDatasetRepo(unittest.TestCase):

    test_dataset1 = {
        'id': 'basicstats-census',
        'name': 'Basic Stats - Census',
        'provider_id': 'bbva',
        'category_id': 'demographics',
        'country_iso_code3': 'esp',
        'geography_id': 'carto-do-public-data.tiger.geography_esp_census_2019',
        'temporal_aggregations': '5yrs',
        'time_coverage': ['2006-01-01', '2010-01-01'],
        'group_id': 'basicstats_esp_2019',
        'version': '20190203',
        'is_public': True
    }
    test_dataset2 = {
        'id': 'basicstats-municipalities',
        'name': 'Basic Stats - Municipalities',
        'provider_id': 'bbva',
        'category_id': 'demographics',
        'country_iso_code3': 'esp',
        'geography_id': 'carto-do-public-data.tiger.geography_esp_municipalities_2019',
        'temporal_aggregations': '5yrs',
        'time_coverage': ['2006-01-01', '2010-01-01'],
        'group_id': 'basicstats_esp_2019',
        'version': '20190203',
        'is_public': False
    }

    def setUp(self):
        mocked_sql_result = [{
            'id': 'basicstats-census',
            'name': 'Basic Stats - Census',
            'provider_id': 'bbva',
            'category_id': 'demographics',
            'country_iso_code3': 'esp',
            'geography_id': 'carto-do-public-data.tiger.geography_esp_census_2019',
            'temporalaggregations': '5yrs',
            'time_coverage': ['2006-01-01', '2010-01-01'],
            'datasets_groups_id': 'basicstats_esp_2019',
            'version': '20190203',
            'is_public_data': True
        }, {
            'id': 'basicstats-municipalities',
            'name': 'Basic Stats - Municipalities',
            'provider_id': 'bbva',
            'category_id': 'demographics',
            'country_iso_code3': 'esp',
            'geography_id': 'carto-do-public-data.tiger.geography_esp_municipalities_2019',
            'temporalaggregations': '5yrs',
            'time_coverage': ['2006-01-01', '2010-01-01'],
            'datasets_groups_id': 'basicstats_esp_2019',
            'version': '20190203',
            'is_public_data': False
        }]

        RepoClient.get_datasets = Mock(return_value=mocked_sql_result)

    def test_get_all(self):
        # Given
        repo = DatasetRepository()

        # When
        datasets = repo.get_all()

        # Then
        expected_datasets = [self.test_dataset1, self.test_dataset2]
        assert datasets == expected_datasets

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_datasets = Mock(return_value=[])
        repo = DatasetRepository()

        # When
        datasets = repo.get_all()

        # Then
        assert datasets == []

    def test_get_by_id(self,):
        # Given
        requested_id = self.test_dataset1['id']
        repo = DatasetRepository()

        # When
        dataset = repo.get_by_id(requested_id)

        # Then
        assert dataset == self.test_dataset1

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_datasets = Mock(return_value=[])
        requested_id = 'unknown_id'
        repo = DatasetRepository()

        # When
        dataset = repo.get_by_id(requested_id)

        # Then
        assert dataset is None
