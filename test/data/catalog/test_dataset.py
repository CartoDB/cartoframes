import unittest
import pandas as pd

from cartoframes.data.catalog.dataset import Datasets
from cartoframes.data.catalog.repository.dataset_repo import DatasetRepository

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


@patch.object(DatasetRepository, 'get_all')
class TestDatasets(unittest.TestCase):

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
    expected_datasets = [test_dataset1, test_dataset2]

    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = self.expected_datasets

        # When
        datasets = Datasets.get_all()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)
