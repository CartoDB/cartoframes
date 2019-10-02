import unittest
import pandas as pd

from cartoframes.data.observatory.variable import Variables
from cartoframes.data.observatory.dataset import Datasets, Dataset
from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository
from cartoframes.exceptions import DiscoveryException

from .examples import test_dataset1, test_datasets, test_variables, db_dataset1

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
        dataset = Dataset.get_by_id(test_dataset1['id'])

        # Then
        assert isinstance(dataset, pd.Series)
        assert isinstance(dataset, Dataset)
        assert dataset == test_dataset1

    @patch.object(VariableRepository, 'get_by_dataset')
    def test_get_variables_by_dataset(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        variables = test_dataset1.variables()

        # Then
        assert isinstance(variables, pd.DataFrame)
        assert isinstance(variables, Variables)
        assert variables == test_variables

    def test_get_variables_by_dataset_fails_if_column_Series(self):
        # Given
        dataset = test_datasets.id

        # Then
        with self.assertRaises(DiscoveryException):
            dataset.variables()


class TestDatasets(unittest.TestCase):

    @patch.object(DatasetRepository, 'get_all')
    def test_get_all_datasets(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = Datasets.get_all()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)

    @patch.object(DatasetRepository, 'get_by_id')
    def test_get_dataset_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_dataset1

        # When
        dataset = Datasets.get_by_id(test_dataset1['id'])

        # Then
        assert isinstance(dataset, pd.Series)
        assert isinstance(dataset, Dataset)
        assert dataset == test_dataset1

    @patch.object(DatasetRepository, 'get_all')
    def test_datasets_are_indexed_with_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets
        dataset_id = db_dataset1['id']

        # When
        datasets = Datasets.get_all()
        dataset = datasets.loc[dataset_id]

        # Then
        assert dataset == test_dataset1

    @patch.object(DatasetRepository, 'get_all')
    def test_datasets_slice_is_dataset_and_series(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = Datasets.get_all()
        dataset = datasets.iloc[0]

        # Then
        assert isinstance(dataset, Dataset)
        assert isinstance(dataset, pd.Series)
