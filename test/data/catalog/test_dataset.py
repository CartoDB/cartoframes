import unittest
import pandas as pd

from cartoframes.data.catalog.variable import Variables
from cartoframes.data.catalog.dataset import Datasets, Dataset
from cartoframes.data.catalog.repository.variable_repo import VariableRepository
from cartoframes.data.catalog.repository.dataset_repo import DatasetRepository

from .examples import test_dataset1, test_datasets, test_variables

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestDataset(unittest.TestCase):

    @patch.object(DatasetRepository, 'get_by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_dataset1

        # When
        dataset = Dataset.get_by_id(test_dataset1['id'])

        # Then
        assert isinstance(dataset, pd.Series)
        assert isinstance(dataset, Dataset)
        assert dataset == test_dataset1

    @patch.object(VariableRepository, 'get_by_dataset')
    def test_get_variables(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        variables = test_dataset1.variables

        # Then
        assert isinstance(variables, pd.DataFrame)
        assert isinstance(variables, Variables)
        assert variables == test_variables


class TestDatasets(unittest.TestCase):

    @patch.object(DatasetRepository, 'get_all')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = Datasets.get_all()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)

    @patch.object(DatasetRepository, 'get_by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_dataset1

        # When
        dataset = Datasets.get_by_id(test_dataset1['id'])

        # Then
        assert isinstance(dataset, pd.Series)
        assert isinstance(dataset, Dataset)
        assert dataset == test_dataset1
