import unittest

from cartoframes.data.catalog.category import Categories
from cartoframes.data.catalog.country import Countries
from cartoframes.data.catalog.do import DO
from data.catalog.examples import test_country2, test_country1, test_category1, test_category2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestDO(unittest.TestCase):

    @patch.object(Countries, 'get_all')
    def test_countries(self, mocked_countries):
        # Given
        expected_countries = [test_country1, test_country2]
        mocked_countries.return_value = expected_countries
        do = DO()

        # When
        countries = do.countries

        # Then
        assert countries == expected_countries

    @patch.object(Categories, 'get_all')
    def test_categories(self, mocked_categories):
        # Given
        expected_categories = [test_category1, test_category2]
        mocked_categories.return_value = expected_categories
        do = DO()

        # When
        categories = do.categories

        # Then
        assert categories == expected_categories
