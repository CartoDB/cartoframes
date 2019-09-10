import unittest
import pandas as pd

from cartoframes.data.catalog.geography import Geographies
from cartoframes.data.catalog.dataset import Datasets
from cartoframes.data.catalog.category import Categories
from cartoframes.data.catalog.country import Countries, Country
from cartoframes.data.catalog.repository.geography_repo import GeographyRepository
from cartoframes.data.catalog.repository.category_repo import CategoryRepository
from cartoframes.data.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.catalog.repository.country_repo import CountryRepository

from .examples import test_country1, test_datasets, test_countries, test_categories, \
    test_geographies

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestCountry(unittest.TestCase):

    @patch.object(CountryRepository, 'get_by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_country1

        # When
        country = Country.get_by_id('esp')

        # Then
        assert isinstance(country, pd.Series)
        assert isinstance(country, Country)
        assert country == test_country1

    @patch.object(DatasetRepository, 'get_by_country')
    def test_get_datasets(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_country1.datasets

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets

    @patch.object(CategoryRepository, 'get_by_country')
    def test_get_categories(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_categories

        # When
        categories = test_country1.categories

        # Then
        assert isinstance(categories, pd.DataFrame)
        assert isinstance(categories, Categories)
        assert categories == test_categories

    @patch.object(GeographyRepository, 'get_by_country')
    def test_get_geographies(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies

        # When
        geographies = test_country1.geographies

        # Then
        assert isinstance(geographies, pd.DataFrame)
        assert isinstance(geographies, Geographies)
        assert geographies == test_geographies


class TestCountries(unittest.TestCase):

    @patch.object(CountryRepository, 'get_all')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_countries

        # When
        countries = Countries.get_all()

        # Then
        assert isinstance(countries, pd.DataFrame)
        assert isinstance(countries, Countries)
        assert countries == test_countries

    @patch.object(CountryRepository, 'get_by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_country1

        # When
        country = Countries.get_by_id('esp')

        # Then
        assert isinstance(country, pd.Series)
        assert isinstance(country, Country)
        assert country == test_country1
