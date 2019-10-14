import unittest
import pandas as pd

from google.api_core.exceptions import NotFound

from carto.exceptions import CartoException

from cartoframes.data.observatory.entity import CatalogList
from cartoframes.data.observatory.geography import Geography
from cartoframes.data.observatory.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository
from .examples import test_geography1, test_geographies, test_datasets, db_geography1, test_geography2, db_geography2
from .mocks import BigQueryClientMock, CredentialsMock

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

    def test_get_geography_by_id_from_geographies_list(self):
        # Given
        geographies = CatalogList([test_geography1, test_geography2])

        # When
        geography = geographies.get(test_geography1.id)

        # Then
        assert isinstance(geography, object)
        assert isinstance(geography, Geography)
        assert geography == test_geography1

    def test_get_geography_by_slug_from_geographies_list(self):
        # Given
        geographies = CatalogList([test_geography1, test_geography2])

        # When
        geography = geographies.get(test_geography1.slug)

        # Then
        assert isinstance(geography, object)
        assert isinstance(geography, Geography)
        assert geography == test_geography1

    @patch.object(DatasetRepository, 'get_all')
    def test_get_datasets_by_geography(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_geography1.datasets

        # Then
        mocked_repo.assert_called_once_with({'geography_id': test_geography1.id})
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    def test_geography_properties(self):
        # Given
        geography = Geography(db_geography1)

        # When
        geography_id = geography.id
        slug = geography.slug
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
        assert slug == db_geography1['slug']
        assert name == db_geography1['name']
        assert description == db_geography1['description']
        assert country == db_geography1['country_id']
        assert language == db_geography1['lang']
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

    def test_geography_is_exported_as_dict(self):
        # Given
        geography = Geography(db_geography1)
        expected_dict = {key: value for key, value in db_geography1.items() if key is not 'summary_jsonb'}

        # When
        geography_dict = geography.to_dict()

        # Then
        assert isinstance(geography_dict, dict)
        assert geography_dict == expected_dict

    def test_geography_is_represented_with_id(self):
        # Given
        geography = Geography(db_geography1)

        # When
        geography_repr = repr(geography)

        # Then
        assert geography_repr == "<Geography('{id}')>".format(id=db_geography1['slug'])

    def test_geography_is_printed_with_classname(self):
        # Given
        geography = Geography(db_geography1)

        # When
        geography_str = str(geography)

        # Then
        assert geography_str == 'Geography({dict_str})'.format(dict_str=str(db_geography1))

    @patch.object(GeographyRepository, 'get_all')
    def test_get_all_geographies(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies

        # When
        geographies = Geography.get_all()

        # Then
        assert isinstance(geographies, list)
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    def test_geography_list_is_printed_with_classname(self):
        # Given
        geographies = CatalogList([test_geography1, test_geography2])

        # When
        categories_str = str(geographies)

        # Then
        assert categories_str == "[<Geography('{id1}')>, <Geography('{id2}')>]" \
                                 .format(id1=db_geography1['slug'], id2=db_geography2['slug'])

    def test_geography_list_is_represented_with_ids(self):
        # Given
        geographies = CatalogList([test_geography1, test_geography2])

        # When
        categories_repr = repr(geographies)

        # Then
        assert categories_repr == "[<Geography('{id1}')>, <Geography('{id2}')>]"\
                                  .format(id1=db_geography1['slug'], id2=db_geography2['slug'])

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

    @patch.object(GeographyRepository, 'get_by_id')
    @patch('cartoframes.data.observatory.entity._get_bigquery_client')
    def test_dataset_download(self, mocked_bq_client, mocked_repo):
        # mock geography
        mocked_repo.return_value = test_geography1

        # mock big query client
        file_path = 'fake_path'
        mocked_bq_client.return_value = BigQueryClientMock(file_path)

        # test
        username = 'fake_user'
        credentials = CredentialsMock(username)

        dataset = Geography.get(test_geography1.id)
        response = dataset.download(credentials)

        assert response == file_path

    @patch.object(GeographyRepository, 'get_by_id')
    @patch('cartoframes.data.observatory.entity._get_bigquery_client')
    def test_dataset_download_raises_with_nonpurchased(self, mocked_bq_client, mocked_repo):
        # mock geography
        mocked_repo.return_value = test_geography1

        # mock big query client
        mocked_bq_client.return_value = BigQueryClientMock(NotFound('Fake error'))

        # test
        username = 'fake_user'
        credentials = CredentialsMock(username)

        dataset = Geography.get(test_geography1.id)
        with self.assertRaises(CartoException):
            dataset.download(credentials)
