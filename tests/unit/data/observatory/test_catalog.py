from cartoframes.data.observatory.country import Country
from cartoframes.data.observatory.category import Category
from cartoframes.data.observatory.dataset import Dataset
from cartoframes.data.observatory.catalog import Catalog
from .examples import test_country2, test_country1, test_category1, test_category2, test_dataset1, test_dataset2

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestCatalog(object):

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
