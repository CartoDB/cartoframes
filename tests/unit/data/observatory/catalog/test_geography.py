import pytest
import pandas as pd

from unittest.mock import patch
from pyrestcli.exceptions import ServerErrorException

from cartoframes.auth import Credentials
from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.geography import Geography
from cartoframes.data.observatory.catalog.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.catalog.subscription_info import SubscriptionInfo
from cartoframes.data.observatory.catalog.repository.constants import GEOGRAPHY_FILTER
from .examples import (
    test_geography1, test_geographies, test_datasets, db_geography1,
    test_geography2, db_geography2, test_subscription_info
)
from carto.do_dataset import DODataset


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

    @patch.object(DatasetRepository, 'get_all')
    def test_get_datasets_by_geography(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_geography1.datasets

        # Then
        mocked_repo.assert_called_once_with({GEOGRAPHY_FILTER: test_geography1.id})
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
        excluded_fields = ['summary_json', 'geom_coverage']
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
        assert geography_str == "<Geography.get('{id}')>".format(id=db_geography1['slug'])

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
        credentials = Credentials('fake_user', '1234')

        # When
        geographies = Geography.get_all(credentials=credentials)

        # Then
        mocked_repo.assert_called_once_with(None, credentials)
        assert isinstance(geographies, list)
        assert isinstance(geographies, CatalogList)
        assert geographies == test_geographies

    @patch.object(GeographyRepository, 'get_all')
    def test_get_all_geographies_credentials_without_do_enabled(self, mocked_repo):
        # Given
        def raise_exception(a, b):
            raise ServerErrorException(['The user does not have Data Observatory enabled'])
        mocked_repo.side_effect = raise_exception
        credentials = Credentials('fake_user', '1234')

        # When
        with pytest.raises(Exception) as e:
            Geography.get_all(credentials=credentials)

        # Then
        assert str(e.value) == (
            'We are sorry, the Data Observatory is not enabled for your account yet. '
            'Please contact your customer success manager or send an email to '
            'sales@carto.com to request access to it.')

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
        expected_geography_df = geography.to_series()
        del expected_geography_df['summary_json']

        # When
        geography_df = geographies.to_dataframe()
        sliced_geography = geography_df.iloc[0]

        # Then
        assert isinstance(geography_df, pd.DataFrame)
        assert isinstance(sliced_geography, pd.Series)
        assert sliced_geography.equals(expected_geography_df)

    @patch.object(GeographyRepository, 'get_all')
    @patch.object(GeographyRepository, 'get_by_id')
    @patch.object(DODataset, 'download_stream')
    def test_geography_download(self, download_stream_mock, get_by_id_mock, get_all_mock):
        # Given
        get_by_id_mock.return_value = test_geography1
        geography = Geography.get(test_geography1.id)
        get_all_mock.return_value = [geography]
        download_stream_mock.return_value = []
        credentials = Credentials('fake_user', '1234')

        # Then
        geography.to_csv('fake_path', credentials)

    @patch.object(GeographyRepository, 'get_all')
    @patch.object(GeographyRepository, 'get_by_id')
    @patch.object(DODataset, 'download_stream')
    def test_geography_download_not_subscribed(self, download_stream_mock, get_by_id_mock, get_all_mock):
        # Given
        get_by_id_mock.return_value = test_geography2  # is private
        get_by_id_mock.return_value = test_geography2
        geography = Geography.get(test_geography2.id)
        get_all_mock.return_value = []
        download_stream_mock.return_value = []
        credentials = Credentials('fake_user', '1234')

        with pytest.raises(Exception) as e:
            geography.to_csv('fake_path', credentials)

        # Then
        assert str(e.value) == (
            'You are not subscribed to this Geography yet. '
            'Please, use the subscribe method first.')

    @patch.object(GeographyRepository, 'get_all')
    @patch.object(GeographyRepository, 'get_by_id')
    @patch.object(DODataset, 'download_stream')
    def test_geography_download_not_subscribed_but_public(self, download_stream_mock, get_by_id_mock, get_all_mock):
        # Given
        get_by_id_mock.return_value = test_geography1  # is public
        geography = Geography.get(test_geography1.id)
        get_all_mock.return_value = []
        download_stream_mock.return_value = []
        credentials = Credentials('fake_user', '1234')

        geography.to_csv('fake_path', credentials)

    @patch.object(GeographyRepository, 'get_all')
    @patch.object(GeographyRepository, 'get_by_id')
    @patch.object(DODataset, 'download_stream')
    def test_geography_download_without_do_enabled(self, download_stream_mock, get_by_id_mock, get_all_mock):
        # Given
        get_by_id_mock.return_value = test_geography1
        geography = Geography.get(test_geography1.id)
        get_all_mock.return_value = []

        def raise_exception(limit=None, order_by=None):
            raise ServerErrorException(['The user does not have Data Observatory enabled'])
        download_stream_mock.side_effect = raise_exception
        credentials = Credentials('fake_user', '1234')

        # When
        with pytest.raises(Exception) as e:
            geography.to_csv('fake_path', credentials)

        # Then
        assert str(e.value) == (
            'We are sorry, the Data Observatory is not enabled for your account yet. '
            'Please contact your customer success manager or send an email to '
            'sales@carto.com to request access to it.')

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch('cartoframes.data.observatory.catalog.utils.display_subscription_form')
    @patch('cartoframes.data.observatory.catalog.utils.display_existing_subscription_message')
    def test_geography_subscribe(self, mock_display_message, mock_display_form, mock_subscription_ids):
        # Given
        expected_id = db_geography1['id']
        expected_subscribed_ids = []
        mock_subscription_ids.return_value = expected_subscribed_ids
        credentials = Credentials('fake_user', '1234')
        geography = Geography(db_geography1)

        # When
        geography.subscribe(credentials)

        # Then
        mock_subscription_ids.assert_called_once_with(credentials, 'geography')
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
        credentials = Credentials('fake_user', '1234')
        geography = Geography(db_geography1)

        # When
        geography.subscribe(credentials)

        # Then
        mock_subscription_ids.assert_called_once_with(credentials, 'geography')
        mock_display_message.assert_called_once_with(expected_id, 'geography')
        assert not mock_display_form.called

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch('cartoframes.data.observatory.catalog.utils.display_subscription_form')
    @patch('cartoframes.auth.defaults.get_default_credentials')
    def test_geography_subscribe_default_credentials(
      self, mocked_credentials, mock_display_form, mock_subscription_ids):
        # Given
        expected_credentials = Credentials('fake_user', '1234')
        mocked_credentials.return_value = expected_credentials
        geography = Geography(db_geography1)

        # When
        geography.subscribe()

        # Then
        mock_subscription_ids.assert_called_once_with(expected_credentials, 'geography')
        mock_display_form.assert_called_once_with(db_geography1['id'], 'geography', expected_credentials)

    def test_geography_subscribe_wrong_credentials(self):
        # Given
        wrong_credentials = 1234
        geography = Geography(db_geography1)

        # When
        with pytest.raises(ValueError) as e:
            geography.subscribe(wrong_credentials)

        # Then
        assert str(e.value) == ('Credentials attribute is required. '
                                'Please pass a `Credentials` instance '
                                'or use the `set_default_credentials` function.')

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch('cartoframes.data.observatory.catalog.utils.display_subscription_form')
    def test_geography_subscribe_without_do_enabled(self, mock_display_form, mock_subscription_ids):
        # Given
        def raise_exception(a, b, c):
            raise ServerErrorException(['The user does not have Data Observatory enabled'])
        mock_display_form.side_effect = raise_exception
        geography = Geography(db_geography1)
        credentials = Credentials('fake_user', '1234')

        # When
        with pytest.raises(Exception) as e:
            geography.subscribe(credentials)

        # Then
        assert str(e.value) == (
            'We are sorry, the Data Observatory is not enabled for your account yet. '
            'Please contact your customer success manager or send an email to '
            'sales@carto.com to request access to it.')

    @patch('cartoframes.data.observatory.catalog.subscription_info.fetch_subscription_info')
    def test_geography_subscription_info(self, mock_fetch):
        # Given
        mock_fetch.return_value = test_subscription_info
        credentials = Credentials('fake_user', '1234')
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
        expected_credentials = Credentials('fake_user', '1234')
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
        assert str(e.value) == ('Credentials attribute is required. '
                                'Please pass a `Credentials` instance '
                                'or use the `set_default_credentials` function.')

    @patch('cartoframes.data.observatory.catalog.subscription_info.fetch_subscription_info')
    def test_geography_subscription_info_without_do_enabled(self, mock_fetch):
        # Given
        def raise_exception(a, b, c):
            raise ServerErrorException(['The user does not have Data Observatory enabled'])
        mock_fetch.side_effect = raise_exception
        geography = Geography(db_geography1)
        credentials = Credentials('fake_user', '1234')

        # When
        with pytest.raises(Exception) as e:
            geography.subscription_info(credentials)

        # Then
        assert str(e.value) == (
            'We are sorry, the Data Observatory is not enabled for your account yet. '
            'Please contact your customer success manager or send an email to '
            'sales@carto.com to request access to it.')
