import unittest
import pandas as pd

from cartoframes.data.observatory.geography import Geography, Geographies
from cartoframes.data.observatory.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.dataset import Datasets
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository
from cartoframes.exceptions import DiscoveryException

from .examples import test_geography1, test_geographies, test_datasets, db_geography1

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestGeography(unittest.TestCase):

    @patch.object(GeographyRepository, 'get_by_id')
    def test_get_geography_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geography1

        # When
        geography = Geography.get_by_id(test_geography1['id'])

        # Then
        assert isinstance(geography, pd.Series)
        assert isinstance(geography, Geography)
        assert geography == test_geography1

    @patch.object(DatasetRepository, 'get_by_geography')
    def test_get_datasets_by_geography(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_geography1.datasets()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets

    def test_get_datasets_by_geography_fails_if_column_Series(self):
        # Given
        geography = test_geographies.id

        # Then
        with self.assertRaises(DiscoveryException):
            geography.datasets()


class TestGeographies(unittest.TestCase):

    @patch.object(GeographyRepository, 'get_all')
    def test_get_all_geographies(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies

        # When
        geographies = Geographies.get_all()

        # Then
        assert isinstance(geographies, pd.DataFrame)
        assert isinstance(geographies, Geographies)
        assert geographies == test_geographies

    @patch.object(GeographyRepository, 'get_by_id')
    def test_get_geography_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geography1

        # When
        geography = Geographies.get_by_id(test_geography1['id'])

        # Then
        assert isinstance(geography, pd.Series)
        assert isinstance(geography, Geography)
        assert geography == test_geography1

    @patch.object(GeographyRepository, 'get_all')
    def test_geographies_are_indexed_with_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies
        geography_id = db_geography1['id']

        # When
        geographies = Geographies.get_all()
        geography = geographies.loc[geography_id]

        # Then
        assert geography == test_geography1

    @patch.object(GeographyRepository, 'get_all')
    def test_geographies_slice_is_geography_and_series(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies

        # When
        geographies = Geographies.get_all()
        geography = geographies.iloc[0]

        # Then
        assert isinstance(geography, Geography)
        assert isinstance(geography, pd.Series)
