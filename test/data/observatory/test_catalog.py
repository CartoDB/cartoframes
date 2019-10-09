import pytest
import unittest

from cartoframes.auth import Credentials
from cartoframes.data.observatory.country import Country
from cartoframes.data.observatory.category import Category
from cartoframes.data.observatory.dataset import Dataset
from cartoframes.data.observatory.geography import Geography
from cartoframes.data.observatory.catalog import Catalog
from .examples import test_country2, test_country1, test_category1, \
    test_category2, test_dataset1, test_dataset2, test_geography1, test_geography2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestCatalog(unittest.TestCase):

    @patch.object(Country, 'get_all')
    def test_countries(self, mocked_countries):
        # Given
        expected_countries = [test_country1, test_country2]
        mocked_countries.return_value = expected_countries
        catalog = Catalog()

        # When
        countries = catalog.countries

        # Then
        assert countries == expected_countries

    @patch.object(Category, 'get_all')
    def test_categories(self, mocked_categories):
        # Given
        expected_categories = [test_category1, test_category2]
        mocked_categories.return_value = expected_categories
        catalog = Catalog()

        # When
        categories = catalog.categories

        # Then
        assert categories == expected_categories

    @patch.object(Dataset, 'get_all')
    def test_datasets(self, mocked_datasets):
        # Given
        expected_datasets = [test_dataset1, test_dataset2]
        mocked_datasets.return_value = expected_datasets
        catalog = Catalog()

        # When
        datasets = catalog.datasets

        # Then
        assert datasets == expected_datasets

    @patch.object(Dataset, 'get_all')
    @patch.object(Geography, 'get_all')
    def test_subscriptions(self, mocked_geographies, mocked_datasets):
        # Given
        expected_datasets = [test_dataset1, test_dataset2]
        expected_geographies = [test_geography1, test_geography2]
        mocked_datasets.return_value = expected_datasets
        mocked_geographies.return_value = expected_geographies
        credentials = Credentials('user', '1234')
        catalog = Catalog()

        # When
        (datasets, geographies) = catalog.subscriptions(credentials)

        # Then
        mocked_datasets.assert_called_once_with(credentials)
        mocked_geographies.assert_called_once_with(credentials)
        assert datasets == expected_datasets
        assert geographies == expected_geographies

    @patch.object(Dataset, 'get_all')
    @patch.object(Geography, 'get_all')
    def test_subscriptions_wrong_param(self, mocked_geographies, mocked_datasets):
        # Given
        wrong_credentials = 1234
        catalog = Catalog()

        # When
        with pytest.raises(ValueError) as e:
            catalog.subscriptions(wrong_credentials)

        # Then
        assert str(e.value) == '`credentials` must be a Credentials class instance'
