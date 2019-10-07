import unittest
import pandas as pd

from cartoframes.data.observatory.entity import CatalogList
from cartoframes.data.observatory.country import Country
from cartoframes.data.observatory.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.repository.country_repo import CountryRepository
from .examples import test_country1, test_datasets, test_countries, test_geographies, db_country1, test_country2, \
    db_country2

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
        country = Country.get('esp')

        # Then
        assert isinstance(country, object)
        assert isinstance(country, Country)
        assert country == test_country1

    @patch.object(DatasetRepository, 'get_by_country')
    def test_get_datasets_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_country1.datasets

        # Then
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(GeographyRepository, 'get_by_country')
    def test_get_geographies_by_country(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies

        # When
        geographies = test_country1.geographies

        # Then
        assert isinstance(geographies, list)
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    def test_country_properties(self):
        # Given
        country = Country(db_country1)

        # When
        country_id = country.id

        # Then
        assert country_id == db_country1['country_iso_code3']

    def test_country_is_exported_as_series(self):
        # Given
        country = Country(db_country1)

        # When
        country_series = country.to_series()

        # Then
        assert isinstance(country_series, pd.Series)
        assert country_series['country_iso_code3'] == country.id

    def test_country_is_exported_as_dict(self):
        # Given
        country = Country(db_country1)

        # When
        country_dict = country.to_dict()

        # Then
        assert isinstance(country_dict, dict)
        assert country_dict == db_country1

    def test_country_is_represented_with_id(self):
        # Given
        country = Country(db_country1)

        # When
        country_repr = repr(country)

        # Then
        assert country_repr == 'Country({id})'.format(id=db_country1['country_iso_code3'])

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

    def test_country_list_is_printed_with_classname(self):
        # Given
        countries = CatalogList([test_country1, test_country2])

        # When
        countries_str = str(countries)

        # Then
        assert countries_str == '[Country({c1}), Country({c2})]'.format(c1=str(db_country1), c2=str(db_country2))

    def test_country_list_is_represented_with_ids(self):
        # Given
        countries = CatalogList([test_country1, test_country2])

        # When
        countries_repr = repr(countries)

        # Then
        assert countries_repr == '[Country({id1}), Country({id2})]'\
                                 .format(id1=db_country1['country_iso_code3'], id2=db_country2['country_iso_code3'])

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
