import pandas as pd

from unittest.mock import patch

from cartoframes.data.observatory.catalog.country import Country
from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.repository.country_repo import CountryRepository
from cartoframes.data.observatory.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.catalog.repository.category_repo import CategoryRepository
from cartoframes.data.observatory.catalog.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.catalog.repository.constants import COUNTRY_FILTER
from .examples import (
    test_country1, test_datasets, test_countries, test_geographies, db_country1, test_country2,
    db_country2, test_categories
)


class TestCountry(object):

    @patch.object(CountryRepository, 'get_by_id')
    def test_get_country_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_country1

        # When
        country = Country.get('esp')

        # Then
        assert isinstance(country, object)
        assert isinstance(country, Country)
        assert country == test_country1

    @patch.object(DatasetRepository, 'get_all')
    def test_get_datasets_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_country1.datasets

        # Then
        mocked_repo.assert_called_once_with({COUNTRY_FILTER: test_country1.id})
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(GeographyRepository, 'get_all')
    def test_get_geographies_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies

        # When
        geographies = test_country1.geographies

        # Then
        mocked_repo.assert_called_once_with({COUNTRY_FILTER: test_country1.id})
        assert isinstance(geographies, list)
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    @patch.object(CategoryRepository, 'get_all')
    def test_get_categories_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_categories

        # When
        categories = test_country1.categories

        # Then
        mocked_repo.assert_called_once_with({COUNTRY_FILTER: test_country1.id})
        assert isinstance(categories, list)
        assert isinstance(categories, CatalogList)
        assert categories == test_categories

    def test_country_properties(self):
        # Given
        country = Country(db_country1)

        # When
        country_id = country.id

        # Then
        assert country_id == db_country1['id']

    def test_country_is_exported_as_series(self):
        # Given
        country = Country(db_country1)

        # When
        country_series = country.to_series()

        # Then
        assert isinstance(country_series, pd.Series)
        assert country_series['id'] == country.id

    def test_country_is_exported_as_dict(self):
        # Given
        country = Country(db_country1)

        # When
        country_dict = country.to_dict()

        # Then
        assert isinstance(country_dict, dict)
        assert country_dict == db_country1

    def test_country_is_represented_with_classname_and_id(self):
        # Given
        country = Country(db_country1)

        # When
        country_repr = repr(country)

        # Then
        assert country_repr == "<Country.get('{id}')> #'{descr}'" \
                               .format(id=db_country1['id'], descr=db_country1['name'])

    def test_country_is_printed_with_classname(self):
        # Given
        country = Country(db_country1)

        # When
        country_str = str(country)

        # Then
        assert country_str == 'Country({dict_str})'.format(dict_str=str(db_country1))

    @patch.object(CountryRepository, 'get_all')
    def test_get_all_countries(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_countries

        # When
        countries = Country.get_all()

        # Then
        assert isinstance(countries, list)
        assert isinstance(countries, CatalogList)
        assert countries == test_countries

    def test_country_list_is_printed_with_classname_and_ids(self):
        # Given
        countries = CatalogList([test_country1, test_country2])

        # When
        countries_str = str(countries)

        # Then
        assert countries_str == "[<Country.get('{id1}')> #'{descr1}', <Country.get('{id2}')> #'{descr2}']" \
                                .format(id1=db_country1['id'], descr1=db_country1['name'],
                                        id2=db_country2['id'], descr2=db_country2['name'])

    def test_country_list_is_represented_with_classname_and_ids(self):
        # Given
        countries = CatalogList([test_country1, test_country2])

        # When
        countries_repr = repr(countries)

        # Then
        assert countries_repr == "[<Country.get('{id1}')> #'{descr1}', <Country.get('{id2}')> #'{descr2}']" \
                                 .format(id1=db_country1['id'], descr1=db_country1['name'],
                                         id2=db_country2['id'], descr2=db_country2['name'])

    def test_countries_items_are_obtained_as_country(self):
        # Given
        countries = test_countries

        # When
        country = countries[0]

        # Then
        assert isinstance(country, Country)
        assert country == test_country1

    def test_countries_are_exported_as_dataframe(self):
        # Given
        countries = test_countries
        country = countries[0]

        # When
        countries_df = countries.to_dataframe()
        sliced_country = countries_df.iloc[0]

        # Then
        assert isinstance(countries_df, pd.DataFrame)
        assert isinstance(sliced_country, pd.Series)
        assert sliced_country.equals(country.to_series())
