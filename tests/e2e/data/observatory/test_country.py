import unittest
import pandas as pd

from cartoframes.data.observatory.geography import Geographies
from cartoframes.data.observatory.dataset import Datasets
from cartoframes.data.observatory.country import Countries, Country
from cartoframes.data.observatory.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.repository.country_repo import CountryRepository
from cartoframes.exceptions import DiscoveryException

from .examples import test_country1, test_datasets, test_countries, test_geographies, db_country1

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestCountry(unittest.TestCase):

    @patch.object(CountryRepository, 'get_by_id')
    def test_get_country_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_country1

        # When
        country = Country.get_by_id('esp')

        # Then
        assert isinstance(country, pd.Series)
        assert isinstance(country, Country)
        assert country == test_country1

    @patch.object(DatasetRepository, 'get_by_country')
    def test_get_datasets_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_country1.datasets()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets

    def test_get_datasets_by_country_fails_if_column_Series(self):
        # Given
        country = test_countries.country_iso_code3

        # Then
        with self.assertRaises(DiscoveryException):
            country.datasets()

    @patch.object(GeographyRepository, 'get_by_country')
    def test_get_geographies_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies

        # When
        geographies = test_country1.geographies()

        # Then
        assert isinstance(geographies, pd.DataFrame)
        assert isinstance(geographies, Geographies)
        assert geographies == test_geographies

    def test_get_geographies_by_country_fails_if_column_Series(self):
        # Given
        country = test_countries.country_iso_code3

        # Then
        with self.assertRaises(DiscoveryException):
            country.geographies()


class TestCountries(unittest.TestCase):

    @patch.object(CountryRepository, 'get_all')
    def test_get_all_countries(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_countries

        # When
        countries = Countries.get_all()

        # Then
        assert isinstance(countries, pd.DataFrame)
        assert isinstance(countries, Countries)
        assert countries == test_countries

    @patch.object(CountryRepository, 'get_by_id')
    def test_get_country_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_country1

        # When
        country = Countries.get_by_id('esp')

        # Then
        assert isinstance(country, pd.Series)
        assert isinstance(country, Country)
        assert country == test_country1

    @patch.object(CountryRepository, 'get_all')
    def test_countries_are_indexed_with_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_countries
        country_id = db_country1['country_iso_code3']

        # When
        countries = Countries.get_all()
        country = countries.loc[country_id]

        # Then
        assert country == test_country1

    @patch.object(CountryRepository, 'get_all')
    def test_countries_slice_is_country_and_series(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_countries

        # When
        countries = Countries.get_all()
        country = countries.iloc[0]

        # Then
        assert isinstance(country, Country)
        assert isinstance(country, pd.Series)
