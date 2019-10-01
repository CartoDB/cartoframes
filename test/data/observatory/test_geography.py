import unittest
import pandas as pd

from cartoframes.data.observatory.geography import Geography, Geographies
from cartoframes.data.observatory.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.dataset import Datasets
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository

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
        geography = Geography.get(test_geography1.id)

        # Then
        assert isinstance(geography, object)
        assert isinstance(geography, Geography)
        assert geography == test_geography1

    @patch.object(DatasetRepository, 'get_by_geography')
    def test_get_datasets_by_geography(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_geography1.datasets()

        # Then
        assert isinstance(datasets, list)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets

    def test_geography_properties(self):
        # Given
        geography = Geography(db_geography1)

        # When
        geography_id = geography.id
        name = geography.name
        description = geography.description
        country = geography.country
        language = geography.language
        provider = geography.provider
        geom_coverage = geography.geom_coverage
        update_frequency = geography.update_frequency
        version = geography.version
        is_public_data = geography.is_public_data
        summary = geography.summary

        # Then
        assert geography_id == db_geography1['id']
        assert name == db_geography1['name']
        assert description == db_geography1['description']
        assert country == db_geography1['country_iso_code3']
        assert language == db_geography1['language_iso_code3']
        assert provider == db_geography1['provider_id']
        assert geom_coverage == db_geography1['geom_coverage']
        assert update_frequency == db_geography1['update_frequency']
        assert version == db_geography1['version']
        assert is_public_data == db_geography1['is_public_data']
        assert summary == db_geography1['summary_jsonb']

    def test_geography_is_exported_as_series(self):
        # Given
        geography = test_geography1

        # When
        geography_series = geography.to_series()

        # Then
        assert isinstance(geography_series, pd.Series)
        assert geography_series['id'] == geography.id


class TestGeographies(unittest.TestCase):

    @patch.object(GeographyRepository, 'get_all')
    def test_get_all_geographies(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies

        # When
        geographies = Geographies.get_all()

        # Then
        assert isinstance(geographies, list)
        assert isinstance(geographies, Geographies)
        assert geographies == test_geographies

    @patch.object(GeographyRepository, 'get_by_id')
    def test_get_geography_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geography1

        # When
        geography = Geographies.get(test_geography1.id)

        # Then
        assert isinstance(geography, object)
        assert isinstance(geography, Geography)
        assert geography == test_geography1

    # @patch.object(GeographyRepository, 'get_all')
    # def test_geographies_are_indexed_with_id(self, mocked_repo):
    #     # Given
    #     mocked_repo.return_value = test_geographies
    #     geography_id = db_geography1['id']
    #
    #     # When
    #     geographies = Geographies.get_all()
    #     geography = geographies.loc[geography_id]
    #
    #     # Then
    #     assert geography == test_geography1

    def test_geographies_items_are_obtained_as_geography(self):
        # Given
        geographies = test_geographies

        # When
        geography = geographies[0]

        # Then
        assert isinstance(geography, Geography)
        assert geography == test_geography1

    def test_geographies_are_exported_as_dataframe(self):
        # Given
        geographies = test_geographies
        geography = geographies[0]

        # When
        geography_df = geographies.to_dataframe()
        sliced_geography = geography_df.iloc[0]

        # Then
        assert isinstance(geography_df, pd.DataFrame)
        assert isinstance(sliced_geography, pd.Series)
        assert sliced_geography.equals(geography.to_series())
