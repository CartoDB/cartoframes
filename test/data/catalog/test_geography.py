import unittest
import pandas as pd
from cartoframes.data.catalog.geography import Geography, Geographies

from cartoframes.data.catalog.repository.geography_repo import GeographyRepository

from cartoframes.data.catalog.dataset import Datasets
from cartoframes.data.catalog.repository.dataset_repo import DatasetRepository

from .examples import test_geography1, test_geographies, test_datasets

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestGeography(unittest.TestCase):

    @patch.object(GeographyRepository, 'get_by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geography1

        # When
        geography = Geography.get_by_id(test_geography1['id'])

        # Then
        assert isinstance(geography, pd.Series)
        assert isinstance(geography, Geography)
        assert geography == test_geography1

    @patch.object(DatasetRepository, 'get_by_geography')
    def test_get_datasets(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_geography1.datasets

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets


class TestGeographies(unittest.TestCase):

    @patch.object(GeographyRepository, 'get_all')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies

        # When
        geographies = Geographies.get_all()

        # Then
        assert isinstance(geographies, pd.DataFrame)
        assert isinstance(geographies, Geographies)
        assert geographies == test_geographies

    @patch.object(GeographyRepository, 'get_by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geography1

        # When
        geography = Geographies.get_by_id(test_geography1['id'])

        # Then
        assert isinstance(geography, pd.Series)
        assert isinstance(geography, Geography)
        assert geography == test_geography1
