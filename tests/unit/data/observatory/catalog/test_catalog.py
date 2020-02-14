import pytest

from unittest.mock import patch

from cartoframes.auth import Credentials
from cartoframes.data.observatory.catalog.dataset import Dataset
from cartoframes.data.observatory.catalog.geography import Geography
from cartoframes.data.observatory.catalog.country import Country
from cartoframes.data.observatory.catalog.category import Category
from cartoframes.data.observatory.catalog.catalog import Catalog
from cartoframes.data.observatory.catalog.subscriptions import Subscriptions
from cartoframes.data.observatory.catalog.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.catalog.repository.constants import (
    CATEGORY_FILTER, COUNTRY_FILTER, GEOGRAPHY_FILTER
)
from .examples import (
    test_country2, test_country1, test_category1, test_category2, test_dataset1, test_dataset2,
    test_geographies, test_datasets, test_categories, test_countries, test_geography1, test_geography2
)


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

    @patch.object(Country, 'get_all')
    def test_filters_on_countries(self, mocked_countries):
        # Given
        mocked_countries.return_value = test_countries
        catalog = Catalog()

        # When
        countries = catalog.category('demographics').countries

        # Then
        mocked_countries.called_once_with({CATEGORY_FILTER: 'demographics'})
        assert countries == test_countries

    @patch.object(Category, 'get_all')
    def test_filters_on_categories(self, mocked_categories):
        # Given
        mocked_categories.return_value = test_categories
        catalog = Catalog()

        # When
        categories = catalog.country('usa').categories

        # Then
        mocked_categories.called_once_with({COUNTRY_FILTER: 'usa'})
        assert categories == test_categories

    @patch.object(Dataset, 'get_all')
    def test_filters_on_datasets(self, mocked_datasets):
        # Given
        mocked_datasets.return_value = test_datasets
        catalog = Catalog()

        # When
        datasets = catalog.country('usa').category('demographics').datasets

        # Then
        mocked_datasets.called_once_with({COUNTRY_FILTER: 'usa', CATEGORY_FILTER: 'demographics'})
        assert datasets == test_datasets

    @patch.object(Geography, 'get_all')
    def test_filters_on_geographies(self, mocked_geographies):
        # Given
        mocked_geographies.return_value = test_geographies
        catalog = Catalog()

        # When
        geographies = catalog.country('usa').category('demographics').geographies

        # Then
        mocked_geographies.called_once_with({COUNTRY_FILTER: 'usa', CATEGORY_FILTER: 'demographics'})
        assert geographies == test_geographies

    @patch.object(Dataset, 'get_all')
    def test_all_filters(self, mocked_datasets):
        # Given
        mocked_datasets.return_value = test_datasets
        catalog = Catalog()

        # When
        datasets = catalog.country('usa').category('demographics') \
            .geography('carto-do-public-data.tiger.geography_esp_census_2019').datasets

        # Then
        mocked_datasets.called_once_with({
            COUNTRY_FILTER: 'usa',
            CATEGORY_FILTER: 'demographics',
            GEOGRAPHY_FILTER: 'carto-do-public-data.tiger.geography_esp_census_2019'})

        assert datasets == test_datasets

    @patch.object(Dataset, 'get_all')
    @patch.object(GeographyRepository, 'get_by_id')
    def test_geography_filter_by_slug(self, mocked_repo, mocked_datasets):
        # Given
        mocked_repo.return_value = test_geography1
        mocked_datasets.return_value = test_datasets
        slug = 'esp_census_2019_4567890d'
        catalog = Catalog()

        # When
        datasets = catalog.geography(slug).datasets

        # Then
        mocked_repo.assert_called_once_with(slug)
        mocked_datasets.assert_called_once_with({GEOGRAPHY_FILTER: test_geography1.id})
        assert datasets == test_datasets

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
        subscriptions = catalog.subscriptions(credentials)

        # Then
        mocked_datasets.assert_called_once_with({}, credentials)
        mocked_geographies.assert_called_once_with({}, credentials)
        assert isinstance(subscriptions, Subscriptions)
        assert subscriptions.datasets == expected_datasets
        assert subscriptions.geographies == expected_geographies

    @patch.object(Dataset, 'get_all')
    @patch.object(Geography, 'get_all')
    @patch('cartoframes.auth.defaults.get_default_credentials')
    def test_subscriptions_default_credentials(self, mocked_credentials, mocked_geographies, mocked_datasets):
        # Given
        expected_datasets = [test_dataset1, test_dataset2]
        expected_geographies = [test_geography1, test_geography2]
        expected_credentials = Credentials('user', '1234')
        mocked_datasets.return_value = expected_datasets
        mocked_geographies.return_value = expected_geographies
        mocked_credentials.return_value = expected_credentials
        catalog = Catalog()

        # When
        subscriptions = catalog.subscriptions()

        # Then
        mocked_datasets.assert_called_once_with({}, expected_credentials)
        mocked_geographies.assert_called_once_with({}, expected_credentials)
        assert isinstance(subscriptions, Subscriptions)
        assert subscriptions.datasets == expected_datasets
        assert subscriptions.geographies == expected_geographies

    @patch.object(Dataset, 'get_all')
    @patch.object(Geography, 'get_all')
    def test_subscriptions_wrong_credentials(self, mocked_geographies, mocked_datasets):
        # Given
        wrong_credentials = 1234
        catalog = Catalog()

        # When
        with pytest.raises(ValueError) as e:
            catalog.subscriptions(wrong_credentials)

        # Then
        assert str(e.value) == ('Credentials attribute is required. '
                                'Please pass a `Credentials` instance '
                                'or use the `set_default_credentials` function.')
