import unittest
import pandas as pd
from cartoframes.data.observatory.variable_group import VariablesGroups

from cartoframes.data.observatory.variable import Variables
from cartoframes.data.observatory.dataset import Datasets, Dataset
from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.variable_group_repo import VariableGroupRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository

from .examples import test_dataset1, test_datasets, test_variables, test_variables_groups, db_dataset1

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

    @patch.object(VariableRepository, 'get_by_dataset')
    def test_get_variables_by_dataset(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        variables = test_dataset1.variables()

        # Then
        assert isinstance(variables, list)
        assert isinstance(variables, Variables)
        assert variables == test_variables

    @patch.object(VariableGroupRepository, 'get_by_dataset')
    def test_get_variables_groups_by_dataset(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables_groups

        # When
        variables_groups = test_dataset1.variables_groups()

        # Then
        assert isinstance(variables_groups, list)
        assert isinstance(variables_groups, VariablesGroups)
        assert variables_groups == test_variables_groups

    def test_dataset_properties(self):
        # Given
        dataset = Dataset(db_dataset1)

        # When
        dataset_id = dataset.id
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
        assert name == db_dataset1['name']
        assert description == db_dataset1['description']
        assert provider == db_dataset1['provider_id']
        assert category == db_dataset1['category_id']
        assert data_source == db_dataset1['data_source_id']
        assert country == db_dataset1['country_iso_code3']
        assert language == db_dataset1['language_iso_code3']
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


class TestDatasets(unittest.TestCase):

    @patch.object(DatasetRepository, 'get_all')
    def test_get_all_datasets(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = Datasets.get_all()

        # Then
        assert isinstance(datasets, list)
        assert isinstance(datasets, Datasets)

    @patch.object(DatasetRepository, 'get_by_id')
    def test_get_dataset_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_dataset1

        # When
        dataset = Datasets.get(test_dataset1.id)

        # Then
        assert isinstance(dataset, object)
        assert isinstance(dataset, Dataset)
        assert dataset == test_dataset1

    # @patch.object(DatasetRepository, 'get_all')
    # def test_datasets_are_indexed_with_id(self, mocked_repo):
    #     # Given
    #     mocked_repo.return_value = test_datasets
    #     dataset_id = db_dataset1['id']
    #
    #     # When
    #     datasets = Datasets.get_all()
    #     dataset = datasets.loc[dataset_id]
    #
    #     # Then
    #     assert dataset == test_dataset1

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
