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
        sql_datasets = [{
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

        RepoClient.get_datasets = Mock(return_value=sql_datasets)

    def test_get_all(self):
        # When
        repo = DatasetRepository()
        datasets = repo.get_all()

        # Then
        expected_datasets = [self.test_dataset1, self.test_dataset2]
        self.assertEqual(expected_datasets, datasets)

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_datasets = Mock(return_value=[])

        # When
        repo = DatasetRepository()
        datasets = repo.get_all()

        # Then
        self.assertEqual([], datasets)

    def test_get_by_id(self):
        # Given
        requested_id = self.test_dataset1['id']

        # When
        repo = DatasetRepository()
        dataset = repo.get_by_id(requested_id)

        # Then
        self.assertEqual(self.test_dataset1, dataset)

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_datasets = Mock(return_value=[])
        requested_id = 'unknown_id'

        # When
        repo = DatasetRepository()
        dataset = repo.get_by_id(requested_id)

        # Then
        self.assertEqual(None, dataset)
