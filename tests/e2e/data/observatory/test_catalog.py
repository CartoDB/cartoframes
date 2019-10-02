import unittest

from cartoframes.data.observatory.category import Categories
from cartoframes.data.observatory.country import Countries
from cartoframes.data.observatory.catalog import Catalog
from .examples import test_country2, test_country1, test_category1, test_category2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestCatalog(unittest.TestCase):

    @patch.object(Countries, 'get_all')
    def test_countries(self, mocked_countries):
        # Given
        expected_countries = [test_country1, test_country2]
        mocked_countries.return_value = expected_countries
        catalog = Catalog()

        # When
        countries = catalog.countries()

        # Then
        assert countries == expected_countries

    @patch.object(Categories, 'get_all')
    def test_categories(self, mocked_categories):
        # Given
        expected_categories = [test_category1, test_category2]
        mocked_categories.return_value = expected_categories
        catalog = Catalog()

        # When
        categories = catalog.categories()

        # Then
        assert categories == expected_categories
