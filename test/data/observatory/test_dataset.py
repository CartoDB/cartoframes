import unittest
import pandas as pd

from google.api_core.exceptions import NotFound

from carto.exceptions import CartoException

from cartoframes.auth import Credentials
from cartoframes.data.observatory.entity import CatalogList
from cartoframes.data.observatory.dataset import Dataset
from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.variable_group_repo import VariableGroupRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository
from .examples import test_dataset1, test_datasets, test_variables, test_variables_groups, db_dataset1, test_dataset2, \
    db_dataset2
from .mocks import BigQueryClientMock, CredentialsMock

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestDataset(unittest.TestCase):

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

    def test_get_dataset_by_id_from_datasets_list(self):
        # Given
        datasets = CatalogList([test_dataset1, test_dataset2])

        # When
        dataset = datasets.get(test_dataset1.id)

        # Then
        assert isinstance(dataset, object)
        assert isinstance(dataset, Dataset)
        assert dataset == test_dataset1

    def test_get_dataset_by_slug_from_datasets_list(self):
        # Given
        datasets = CatalogList([test_dataset1, test_dataset2])

        # When
        dataset = datasets.get(test_dataset1.slug)

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
        mocked_repo.assert_called_once_with({'dataset_id': test_dataset1.id})
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
        mocked_repo.assert_called_once_with({'dataset_id': test_dataset1.id})
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
        assert summary == db_dataset1['summary_jsonb']

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
        expected_dict = {key: value for key, value in db_dataset1.items() if key is not 'summary_jsonb'}

        # When
        dataset_dict = dataset.to_dict()

        # Then
        assert isinstance(dataset_dict, dict)
        assert dataset_dict == expected_dict

    def test_dataset_is_represented_with_id(self):
        # Given
        dataset = Dataset(db_dataset1)

        # When
        dataset_repr = repr(dataset)

        # Then
        assert dataset_repr == "<Dataset('{id}')>".format(id=db_dataset1['slug'])

    def test_dataset_is_printed_with_classname(self):
        # Given
        dataset = Dataset(db_dataset1)

        # When
        dataset_str = str(dataset)

        # Then
        assert dataset_str == 'Dataset({dict_str})'.format(dict_str=str(db_dataset1))

    @patch.object(DatasetRepository, 'get_all')
    def test_get_all_datasets(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = Dataset.get_all()

        # Then
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)

    @patch.object(DatasetRepository, 'get_all')
    def test_get_all_datasets_credentials(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets
        credentials = Credentials('user', '1234')

        # When
        datasets = Dataset.get_all(credentials=credentials)

        # Then
        mocked_repo.assert_called_once_with(None, credentials)
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)

    def test_dataset_list_is_printed_with_classname(self):
        # Given
        datasets = CatalogList([test_dataset1, test_dataset2])

        # When
        datasets_str = str(datasets)

        # Then
        assert datasets_str == "[<Dataset('{id1}')>, <Dataset('{id2}')>]"\
                               .format(id1=db_dataset1['slug'], id2=db_dataset2['slug'])

    def test_dataset_list_is_represented_with_slugs(self):
        # Given
        datasets = CatalogList([test_dataset1, test_dataset2])

        # When
        datasets_repr = repr(datasets)

        # Then
        assert datasets_repr == "[<Dataset('{id1}')>, <Dataset('{id2}')>]"\
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

        # When
        dataset_df = datasets.to_dataframe()
        sliced_dataset = dataset_df.iloc[0]

        # Then
        assert isinstance(dataset_df, pd.DataFrame)
        assert isinstance(sliced_dataset, pd.Series)
        assert sliced_dataset.equals(dataset.to_series())

    @patch.object(DatasetRepository, 'get_by_id')
    @patch('cartoframes.data.observatory.entity._get_bigquery_client')
    def test_dataset_download(self, mocked_bq_client, mocked_repo):
        # mock dataset
        mocked_repo.return_value = test_dataset1

        # mock big query client
        file_path = 'fake_path'
        mocked_bq_client.return_value = BigQueryClientMock(file_path)

        # test
        username = 'fake_user'
        credentials = CredentialsMock(username)

        dataset = Dataset.get(test_dataset1.id)
        response = dataset.download(credentials)

        assert response == file_path

    @patch.object(DatasetRepository, 'get_by_id')
    @patch('cartoframes.data.observatory.entity._get_bigquery_client')
    def test_dataset_download_raises_with_nonpurchased(self, mocked_bq_client, mocked_repo):
        # mock dataset
        mocked_repo.return_value = test_dataset1

        # mock big query client
        mocked_bq_client.return_value = BigQueryClientMock(NotFound('Fake error'))

        # test
        username = 'fake_user'
        credentials = CredentialsMock(username)

        dataset = Dataset.get(test_dataset1.id)
        with self.assertRaises(CartoException):
            dataset.download(credentials)
