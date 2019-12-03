import pytest
import pandas as pd

from google.api_core.exceptions import NotFound

from carto.exceptions import CartoException

from cartoframes.auth import Credentials
from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.geography import Geography
from cartoframes.data.observatory.catalog.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.catalog.subscription_info import SubscriptionInfo
from .examples import test_geography1, test_geographies, test_datasets, db_geography1, \
    test_geography2, db_geography2, test_subscription_info
from .mocks import BigQueryClientMock

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestGeography(object):

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
        assert summary == db_geography1['summary_json']

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
        excluded_fields = ['summary_json', 'available_in', 'geom_coverage']
        expected_dict = {key: value for key, value in db_geography1.items() if key not in excluded_fields}

        # When
        geography_dict = geography.to_dict()

        # Then
        assert isinstance(geography_dict, dict)
        assert geography_dict == expected_dict

    def test_geography_is_represented_with_classname_and_slug(self):
        # Given
        geography = Geography(db_geography1)

        # When
        geography_repr = repr(geography)

        # Then
        assert geography_repr == "<Geography.get('{id}')>".format(id=db_geography1['slug'])

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

    @patch.object(GeographyRepository, 'get_all')
    def test_get_all_geographies_credentials(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_geographies
        credentials = Credentials('user', '1234')

        # When
        geographies = Geography.get_all(credentials=credentials)

        # Then
        mocked_repo.assert_called_once_with(None, credentials)
        assert isinstance(geographies, list)
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    def test_geography_list_is_printed_with_classname_and_slugs(self):
        # Given
        geographies = CatalogList([test_geography1, test_geography2])

        # When
        categories_str = str(geographies)

        # Then
        assert categories_str == "[<Geography.get('{id1}')>, <Geography.get('{id2}')>]" \
                                 .format(id1=db_geography1['slug'], id2=db_geography2['slug'])

    def test_geography_list_is_represented_with_classname_and_slugs(self):
        # Given
        geographies = CatalogList([test_geography1, test_geography2])

        # When
        categories_repr = repr(geographies)

        # Then
        assert categories_repr == "[<Geography.get('{id1}')>, <Geography.get('{id2}')>]"\
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

    @patch.object(GeographyRepository, 'get_all')
    @patch.object(GeographyRepository, 'get_by_id')
    @patch('cartoframes.data.observatory.catalog.entity._get_bigquery_client')
    def test_geography_download(self, mocked_bq_client, get_by_id_mock, get_all_mock):
        # mock geography
        get_by_id_mock.return_value = test_geography1
        geography = Geography.get(test_geography1.id)

        # mock subscriptions
        get_all_mock.return_value = [geography]

        # mock big query client
        file_path = 'fake_path'
        mocked_bq_client.return_value = BigQueryClientMock(file_path)

        # test
        credentials = Credentials('fake_user', '1234')

        response = geography.download(credentials)

        assert response == file_path

    @patch.object(GeographyRepository, 'get_all')
    @patch.object(GeographyRepository, 'get_by_id')
    @patch('cartoframes.data.observatory.catalog.entity._get_bigquery_client')
    def test_geography_not_available_in_bq_download_fails(self, mocked_bq_client, get_by_id_mock, get_all_mock):
        # mock geography
        get_by_id_mock.return_value = test_geography2
        geography = Geography.get(test_geography2.id)

        # mock subscriptions
        get_all_mock.return_value = [geography]

        # mock big query client
        file_path = 'fake_path'
        mocked_bq_client.return_value = BigQueryClientMock(file_path)

        # test
        credentials = Credentials('fake_user', '1234')

        with pytest.raises(CartoException) as e:
            geography.download(credentials)

        error = '{} is not ready for Download. Please, contact us for more information.'.format(geography)
        assert str(e.value) == error

    @patch.object(GeographyRepository, 'get_all')
    @patch.object(GeographyRepository, 'get_by_id')
    @patch('cartoframes.data.observatory.catalog.entity._get_bigquery_client')
    def test_geography_not_subscribed_download_fails(self, mocked_bq_client, get_by_id_mock, get_all_mock):
        # mock dataset
        get_by_id_mock.return_value = test_geography2
        geography = Geography.get(test_geography2.id)

        # mock subscriptions
        get_all_mock.return_value = []

        # mock big query client
        file_path = 'fake_path'
        mocked_bq_client.return_value = BigQueryClientMock(file_path)

        # test
        credentials = Credentials('fake_user', '1234')

        with pytest.raises(CartoException) as e:
            geography.download(credentials)

        error = 'You are not subscribed to this Geography yet. Please, use the subscribe method first.'
        assert str(e.value) == error

    @patch.object(GeographyRepository, 'get_all')
    @patch.object(GeographyRepository, 'get_by_id')
    @patch('cartoframes.data.observatory.catalog.entity._get_bigquery_client')
    def test_geography_not_subscribed_but_public_download_works(self, mocked_bq_client, get_by_id_mock, get_all_mock):
        # mock dataset
        get_by_id_mock.return_value = test_geography1  # is public
        geography = Geography.get(test_geography1.id)

        # mock subscriptions
        get_all_mock.return_value = []

        # mock big query client
        file_path = 'fake_path'
        mocked_bq_client.return_value = BigQueryClientMock(file_path)

        # test
        credentials = Credentials('fake_user', '1234')

        response = geography.download(credentials)

        assert response == file_path

    @patch.object(GeographyRepository, 'get_by_id')
    @patch('cartoframes.data.observatory.catalog.entity._get_bigquery_client')
    def test_geography_download_raises_without_do_active(self, mocked_bq_client, mocked_repo):
        # mock geography
        mocked_repo.return_value = test_geography1

        # mock big query client
        mocked_bq_client.return_value = BigQueryClientMock(NotFound('Fake error'))

        # test
        credentials = Credentials('fake_user', '1234')

        geography = Geography.get(test_geography1.id)
        with pytest.raises(CartoException):
            geography.download(credentials)

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch('cartoframes.data.observatory.catalog.utils.display_subscription_form')
    @patch('cartoframes.data.observatory.catalog.utils.display_existing_subscription_message')
    def test_geography_subscribe(self, mock_display_message, mock_display_form, mock_subscription_ids):
        # Given
        expected_id = db_geography1['id']
        expected_subscribed_ids = []
        mock_subscription_ids.return_value = expected_subscribed_ids
        credentials = Credentials('user', '1234')
        geography = Geography(db_geography1)

        # When
        geography.subscribe(credentials)

        # Then
        mock_subscription_ids.assert_called_once_with(credentials)
        mock_display_form.assert_called_once_with(expected_id, 'geography', credentials)
        assert not mock_display_message.called

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch('cartoframes.data.observatory.catalog.utils.display_subscription_form')
    @patch('cartoframes.data.observatory.catalog.utils.display_existing_subscription_message')
    def test_geography_subscribe_existing(self, mock_display_message, mock_display_form, mock_subscription_ids):
        # Given
        expected_id = db_geography1['id']
        expected_subscribed_ids = [expected_id]
        mock_subscription_ids.return_value = expected_subscribed_ids
        credentials = Credentials('user', '1234')
        geography = Geography(db_geography1)

        # When
        geography.subscribe(credentials)

        # Then
        mock_subscription_ids.assert_called_once_with(credentials)
        mock_display_message.assert_called_once_with(expected_id, 'geography')
        assert not mock_display_form.called

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch('cartoframes.data.observatory.catalog.utils.display_subscription_form')
    @patch('cartoframes.auth.defaults.get_default_credentials')
    def test_geography_subscribe_default_credentials(
      self, mocked_credentials, mock_display_form, mock_subscription_ids):
        # Given
        expected_credentials = Credentials('user', '1234')
        mocked_credentials.return_value = expected_credentials
        geography = Geography(db_geography1)

        # When
        geography.subscribe()

        # Then
        mock_subscription_ids.assert_called_once_with(expected_credentials)
        mock_display_form.assert_called_once_with(db_geography1['id'], 'geography', expected_credentials)

    def test_geography_subscribe_wrong_credentials(self):
        # Given
        wrong_credentials = 1234
        geography = Geography(db_geography1)

        # When
        with pytest.raises(ValueError) as e:
            geography.subscribe(wrong_credentials)

        # Then
        assert str(e.value) == '`credentials` must be a Credentials class instance'

    @patch('cartoframes.data.observatory.catalog.subscription_info.fetch_subscription_info')
    def test_geography_subscription_info(self, mock_fetch):
        # Given
        mock_fetch.return_value = test_subscription_info
        credentials = Credentials('user', '1234')
        geography = Geography(db_geography1)

        # When
        info = geography.subscription_info(credentials)

        # Then
        mock_fetch.assert_called_once_with(db_geography1['id'], 'geography', credentials)
        assert isinstance(info, SubscriptionInfo)
        assert info.id == test_subscription_info['id']
        assert info.estimated_delivery_days == test_subscription_info['estimated_delivery_days']
        assert info.subscription_list_price == test_subscription_info['subscription_list_price']
        assert info.tos == test_subscription_info['tos']
        assert info.tos_link == test_subscription_info['tos_link']
        assert info.licenses == test_subscription_info['licenses']
        assert info.licenses_link == test_subscription_info['licenses_link']
        assert info.rights == test_subscription_info['rights']
        assert str(info) == 'Properties: id, estimated_delivery_days, ' + \
                            'subscription_list_price, tos, tos_link, ' + \
                            'licenses, licenses_link, rights'

    @patch('cartoframes.data.observatory.catalog.subscription_info.fetch_subscription_info')
    @patch('cartoframes.auth.defaults.get_default_credentials')
    def test_geography_subscription_info_default_credentials(self, mocked_credentials, mock_fetch):
        # Given
        expected_credentials = Credentials('user', '1234')
        mocked_credentials.return_value = expected_credentials
        geography = Geography(db_geography1)

        # When
        geography.subscription_info()

        # Then
        mock_fetch.assert_called_once_with(db_geography1['id'], 'geography', expected_credentials)

    def test_geography_subscription_info_wrong_credentials(self):
        # Given
        wrong_credentials = 1234
        geography = Geography(db_geography1)

        # When
        with pytest.raises(ValueError) as e:
            geography.subscription_info(wrong_credentials)

        # Then
        assert str(e.value) == '`credentials` must be a Credentials class instance'

    def test_geography_is_available_in(self):
        geography_in_bq = Geography(db_geography1)
        geography_not_in_bq = Geography(db_geography2)

        assert geography_in_bq._is_available_in('bq')
        assert not geography_not_in_bq._is_available_in('bq')

    def test_geography_is_available_in_with_empty_field(self):
        db_geography = dict(db_geography1)
        db_geography['available_in'] = None
        geography_null = Geography(db_geography)
        assert not geography_null._is_available_in('bq')
