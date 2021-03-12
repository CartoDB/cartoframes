import os

import pytest
import pandas as pd

from unittest.mock import patch, ANY
from pyrestcli.exceptions import ServerErrorException

from cartoframes.auth import Credentials
from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.dataset import Dataset
from cartoframes.data.observatory.catalog.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.catalog.repository.variable_group_repo import VariableGroupRepository
from cartoframes.data.observatory.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.catalog.subscription_info import SubscriptionInfo
from cartoframes.data.observatory.catalog.repository.constants import DATASET_FILTER
from .examples import (
    test_dataset1, test_datasets, test_variables, test_variables_groups, db_dataset1, test_dataset2,
    db_dataset2, test_subscription_info
)
from carto.do_dataset import DODataset


class TestDataset(object):

    @patch.object(DatasetRepository, 'get_by_id')
    def test_get_dataset_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_dataset1

        # When
        dataset = Dataset.get(test_dataset1.id)

        # Then
        assert isinstance(dataset, object)
        assert isinstance(dataset, Dataset)
        assert dataset == test_dataset1

    @patch.object(VariableRepository, 'get_all')
    def test_get_variables_by_dataset(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        variables = test_dataset1.variables

        # Then
        mocked_repo.assert_called_once_with({DATASET_FILTER: test_dataset1.id})
        assert isinstance(variables, list)
        assert isinstance(variables, CatalogList)
        assert variables == test_variables

    @patch.object(VariableGroupRepository, 'get_all')
    def test_get_variables_groups_by_dataset(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables_groups

        # When
        variables_groups = test_dataset1.variables_groups

        # Then
        mocked_repo.assert_called_once_with({DATASET_FILTER: test_dataset1.id})
        assert isinstance(variables_groups, list)
        assert isinstance(variables_groups, CatalogList)
        assert variables_groups == test_variables_groups

    def test_dataset_properties(self):
        # Given
        dataset = Dataset(db_dataset1)

        # When
        dataset_id = dataset.id
        slug = dataset.slug
        name = dataset.name
        description = dataset.description
        provider = dataset.provider
        category = dataset.category
        data_source = dataset.data_source
        country = dataset.country
        language = dataset.language
        geography = dataset.geography
        temporal_aggregation = dataset.temporal_aggregation
        time_coverage = dataset.time_coverage
        update_frequency = dataset.update_frequency
        version = dataset.version
        is_public_data = dataset.is_public_data
        summary = dataset.summary

        # Then
        assert dataset_id == db_dataset1['id']
        assert slug == db_dataset1['slug']
        assert name == db_dataset1['name']
        assert description == db_dataset1['description']
        assert provider == db_dataset1['provider_id']
        assert category == db_dataset1['category_id']
        assert data_source == db_dataset1['data_source_id']
        assert country == db_dataset1['country_id']
        assert language == db_dataset1['lang']
        assert geography == db_dataset1['geography_id']
        assert temporal_aggregation == db_dataset1['temporal_aggregation']
        assert time_coverage == db_dataset1['time_coverage']
        assert update_frequency == db_dataset1['update_frequency']
        assert version == db_dataset1['version']
        assert is_public_data == db_dataset1['is_public_data']
        assert summary == db_dataset1['summary_json']

    def test_dataset_is_exported_as_series(self):
        # Given
        dataset = test_dataset1

        # When
        dataset_series = dataset.to_series()

        # Then
        assert isinstance(dataset_series, pd.Series)
        assert dataset_series['id'] == dataset.id

    def test_dataset_is_exported_as_dict(self):
        # Given
        dataset = Dataset(db_dataset1)
        excluded_fields = ['summary_json']
        expected_dict = {key: value for key, value in db_dataset1.items() if key not in excluded_fields}

        # When
        dataset_dict = dataset.to_dict()

        # Then
        assert isinstance(dataset_dict, dict)
        assert dataset_dict == expected_dict

    def test_dataset_is_represented_with_classname_and_slug(self):
        # Given
        dataset = Dataset(db_dataset1)

        # When
        dataset_repr = repr(dataset)

        # Then
        assert dataset_repr == "<Dataset.get('{id}')>".format(id=db_dataset1['slug'])

    def test_dataset_is_printed_with_classname(self):
        # Given
        dataset = Dataset(db_dataset1)

        # When
        dataset_str = str(dataset)

        # Then
        assert dataset_str == "<Dataset.get('{id}')>".format(id=db_dataset1['slug'])

    def test_summary_values(self):
        # Given
        dataset = Dataset(db_dataset2)

        # When
        summary = dataset.summary

        # Then

        assert summary == dataset.data['summary_json']

    def test_summary_head(self):
        # Given
        dataset = Dataset(db_dataset2)

        # When
        summary = dataset.head()

        # Then
        assert isinstance(summary, pd.DataFrame)

    def test_summary_tail(self):
        # Given
        dataset = Dataset(db_dataset2)

        # When
        summary = dataset.tail()

        # Then
        assert isinstance(summary, pd.DataFrame)

    def test_summary_counts(self):
        # Given
        dataset = Dataset(db_dataset2)

        # When
        summary = dataset.counts()

        # Then
        assert isinstance(summary, pd.Series)

    def test_summary_fields_by_type(self):
        # Given
        dataset = Dataset(db_dataset2)

        # When
        summary = dataset.fields_by_type()

        # Then
        assert isinstance(summary, pd.Series)

    @patch.object(pd, 'set_option')
    @patch.object(VariableRepository, 'get_all')
    def test_summary_describe(self, mocked_repo, mocked_set):
        # Given
        dataset = Dataset(db_dataset2)

        # When
        summary = dataset.describe()

        # Then
        assert isinstance(summary, pd.DataFrame)
        mocked_set.assert_called_once_with('display.float_format', ANY)

    @patch.object(pd, 'set_option')
    @patch.object(VariableRepository, 'get_all')
    def test_summary_describe_custom_format(self, mocked_repo, mocked_set):
        # Given
        dataset = Dataset(db_dataset2)

        # When
        summary = dataset.describe(autoformat=False)

        # Then
        assert isinstance(summary, pd.DataFrame)
        mocked_set.assert_not_called()

    @patch.object(DatasetRepository, 'get_all')
    def test_get_all_datasets(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = Dataset.get_all()

        # Then
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(DatasetRepository, 'get_all')
    def test_get_all_datasets_credentials(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets
        credentials = Credentials('fake_user', '1234')

        # When
        datasets = Dataset.get_all(credentials=credentials)

        # Then
        mocked_repo.assert_called_once_with(None, credentials)
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    @patch.object(DatasetRepository, 'get_all')
    def test_get_all_datasets_credentials_without_do_enabled(self, mocked_repo):
        # Given
        def raise_exception(a, b):
            raise ServerErrorException(['The user does not have Data Observatory enabled'])
        mocked_repo.side_effect = raise_exception
        credentials = Credentials('fake_user', '1234')

        # When
        with pytest.raises(Exception) as e:
            Dataset.get_all(credentials=credentials)

        # Then
        assert str(e.value) == (
            'We are sorry, the Data Observatory is not enabled for your account yet. '
            'Please contact your customer success manager or send an email to '
            'sales@carto.com to request access to it.')

    def test_dataset_list_is_printed_with_classname_and_slugs(self):
        # Given
        datasets = CatalogList([test_dataset1, test_dataset2])

        # When
        datasets_str = str(datasets)

        # Then
        assert datasets_str == "[<Dataset.get('{id1}')>, <Dataset.get('{id2}')>]"\
                               .format(id1=db_dataset1['slug'], id2=db_dataset2['slug'])

    def test_dataset_list_is_represented_with_classname_and_slugs(self):
        # Given
        datasets = CatalogList([test_dataset1, test_dataset2])

        # When
        datasets_repr = repr(datasets)

        # Then
        assert datasets_repr == "[<Dataset.get('{id1}')>, <Dataset.get('{id2}')>]"\
                                .format(id1=db_dataset1['slug'], id2=db_dataset2['slug'])

    def test_datasets_items_are_obtained_as_dataset(self):
        # Given
        datasets = test_datasets

        # When
        dataset = datasets[0]

        # Then
        assert isinstance(dataset, Dataset)
        assert dataset == test_dataset1

    def test_datasets_are_exported_as_dataframe(self):
        # Given
        datasets = test_datasets
        dataset = datasets[0]
        expected_dataset_df = dataset.to_series()
        del expected_dataset_df['summary_json']

        # When
        dataset_df = datasets.to_dataframe()
        sliced_dataset = dataset_df.iloc[0]

        # Then
        assert isinstance(dataset_df, pd.DataFrame)
        assert isinstance(sliced_dataset, pd.Series)
        assert sliced_dataset.equals(expected_dataset_df)

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch.object(DatasetRepository, 'get_by_id')
    @patch.object(DODataset, 'download_stream')
    def test_dataset_download(self, mock_download_stream, mock_get_by_id, mock_subscription_ids):
        # Given
        mock_get_by_id.return_value = test_dataset1
        dataset = Dataset.get(test_dataset1.id)
        mock_download_stream.return_value = []
        mock_subscription_ids.return_value = [test_dataset1.id]
        credentials = Credentials('fake_user', '1234')

        # Then
        dataset.to_csv('fake_path', credentials)
        os.remove('fake_path')

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch.object(DatasetRepository, 'get_by_id')
    def test_dataset_not_subscribed_download_not_subscribed(self, mock_get_by_id, mock_subscription_ids):
        # Given
        mock_get_by_id.return_value = test_dataset2  # is private
        dataset = Dataset.get(test_dataset2.id)
        mock_subscription_ids.return_value = []
        credentials = Credentials('fake_user', '1234')

        # When
        with pytest.raises(Exception) as e:
            dataset.to_csv('fake_path', credentials)

        # Then
        assert str(e.value) == (
            'You are not subscribed to this Dataset yet. '
            'Please, use the subscribe method first.')

    @patch.object(DatasetRepository, 'get_by_id')
    @patch.object(DODataset, 'download_stream')
    def test_dataset_download_not_subscribed_but_public(self, mock_download_stream, mock_get_by_id):
        # Given
        mock_get_by_id.return_value = test_dataset1  # is public
        dataset = Dataset.get(test_dataset1.id)
        mock_download_stream.return_value = []
        credentials = Credentials('fake_user', '1234')

        dataset.to_csv('fake_path', credentials)
        os.remove('fake_path')

    @patch.object(DatasetRepository, 'get_by_id')
    @patch.object(DODataset, 'download_stream')
    def test_dataset_download_without_do_enabled(self, mock_download_stream, mock_get_by_id):
        # Given
        mock_get_by_id.return_value = test_dataset1
        dataset = Dataset.get(test_dataset1.id)

        def raise_exception(limit=None, order_by=None, sql_query=None, add_geom=None, is_geography=None):
            raise ServerErrorException(['The user does not have Data Observatory enabled'])
        mock_download_stream.side_effect = raise_exception
        credentials = Credentials('fake_user', '1234')

        # When
        with pytest.raises(Exception) as e:
            dataset.to_csv('fake_path', credentials)

        # Then
        assert str(e.value) == (
            'We are sorry, the Data Observatory is not enabled for your account yet. '
            'Please contact your customer success manager or send an email to '
            'sales@carto.com to request access to it.')

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch('cartoframes.data.observatory.catalog.utils.display_subscription_form')
    @patch('cartoframes.data.observatory.catalog.utils.display_existing_subscription_message')
    def test_dataset_subscribe(self, mock_display_message, mock_display_form, mock_subscription_ids):
        # Given
        expected_id = db_dataset1['id']
        expected_subscribed_ids = []
        mock_subscription_ids.return_value = expected_subscribed_ids
        credentials = Credentials('fake_user', '1234')
        dataset = Dataset(db_dataset1)

        # When
        dataset.subscribe(credentials)

        # Then
        mock_subscription_ids.assert_called_once_with(credentials, 'dataset')
        mock_display_form.assert_called_once_with(expected_id, 'dataset', credentials)
        assert not mock_display_message.called

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch('cartoframes.data.observatory.catalog.utils.display_subscription_form')
    @patch('cartoframes.data.observatory.catalog.utils.display_existing_subscription_message')
    def test_dataset_subscribe_existing(self, mock_display_message, mock_display_form, mock_subscription_ids):
        # Given
        expected_id = db_dataset1['id']
        expected_subscribed_ids = [expected_id]
        mock_subscription_ids.return_value = expected_subscribed_ids
        credentials = Credentials('fake_user', '1234')
        dataset = Dataset(db_dataset1)

        # When
        dataset.subscribe(credentials)

        # Then
        mock_subscription_ids.assert_called_once_with(credentials, 'dataset')
        mock_display_message.assert_called_once_with(expected_id, 'dataset')
        assert not mock_display_form.called

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch('cartoframes.data.observatory.catalog.utils.display_subscription_form')
    @patch('cartoframes.auth.defaults.get_default_credentials')
    def test_dataset_subscribe_default_credentials(self, mock_credentials, mock_display_form, mock_subscription_ids):
        # Given
        expected_credentials = Credentials('fake_user', '1234')
        mock_credentials.return_value = expected_credentials
        dataset = Dataset(db_dataset1)

        # When
        dataset.subscribe()

        # Then
        mock_subscription_ids.assert_called_once_with(expected_credentials, 'dataset')
        mock_display_form.assert_called_once_with(db_dataset1['id'], 'dataset', expected_credentials)

    def test_dataset_subscribe_wrong_credentials(self):
        # Given
        wrong_credentials = 1234
        dataset = Dataset(db_dataset1)

        # When
        with pytest.raises(ValueError) as e:
            dataset.subscribe(wrong_credentials)

        # Then
        assert str(e.value) == ('Credentials attribute is required. '
                                'Please pass a `Credentials` instance '
                                'or use the `set_default_credentials` function.')

    @patch('cartoframes.data.observatory.catalog.subscriptions.get_subscription_ids')
    @patch('cartoframes.data.observatory.catalog.utils.display_subscription_form')
    def test_dataset_subscribe_without_do_enabled(self, mock_display_form, mock_subscription_ids):
        # Given
        def raise_exception(a, b, c):
            raise ServerErrorException(['The user does not have Data Observatory enabled'])
        mock_display_form.side_effect = raise_exception
        dataset = Dataset(db_dataset1)
        credentials = Credentials('fake_user', '1234')

        # When
        with pytest.raises(Exception) as e:
            dataset.subscribe(credentials)

        # Then
        assert str(e.value) == (
            'We are sorry, the Data Observatory is not enabled for your account yet. '
            'Please contact your customer success manager or send an email to '
            'sales@carto.com to request access to it.')

    @patch('cartoframes.data.observatory.catalog.subscription_info.fetch_subscription_info')
    def test_dataset_subscription_info(self, mock_fetch):
        # Given
        mock_fetch.return_value = test_subscription_info
        credentials = Credentials('fake_user', '1234')
        dataset = Dataset(db_dataset1)

        # When
        info = dataset.subscription_info(credentials)

        # Then
        mock_fetch.assert_called_once_with(db_dataset1['id'], 'dataset', credentials)
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
    def test_dataset_subscription_info_default_credentials(self, mock_credentials, mock_fetch):
        # Given
        expected_credentials = Credentials('fake_user', '1234')
        mock_credentials.return_value = expected_credentials
        dataset = Dataset(db_dataset1)

        # When
        dataset.subscription_info()

        # Then
        mock_fetch.assert_called_once_with(db_dataset1['id'], 'dataset', expected_credentials)

    def test_dataset_subscription_info_wrong_credentials(self):
        # Given
        wrong_credentials = 1234
        dataset = Dataset(db_dataset1)

        # When
        with pytest.raises(ValueError) as e:
            dataset.subscription_info(wrong_credentials)

        # Then
        assert str(e.value) == ('Credentials attribute is required. '
                                'Please pass a `Credentials` instance '
                                'or use the `set_default_credentials` function.')

    @patch('cartoframes.data.observatory.catalog.subscription_info.fetch_subscription_info')
    def test_dataset_subscription_info_without_do_enabled(self, mock_fetch):
        # Given
        def raise_exception(a, b, c):
            raise ServerErrorException(['The user does not have Data Observatory enabled'])
        mock_fetch.side_effect = raise_exception
        dataset = Dataset(db_dataset1)
        credentials = Credentials('fake_user', '1234')

        # When
        with pytest.raises(Exception) as e:
            dataset.subscription_info(credentials)

        # Then
        assert str(e.value) == (
            'We are sorry, the Data Observatory is not enabled for your account yet. '
            'Please contact your customer success manager or send an email to '
            'sales@carto.com to request access to it.')
