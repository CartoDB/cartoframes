import unittest
import pandas as pd

from cartoframes.data.observatory.variable import Variables
from cartoframes.data.observatory.dataset import Datasets, Dataset
from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository

from .examples import test_dataset1, test_datasets, test_variables

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestDataset(unittest.TestCase):

    @patch.object(DatasetRepository, 'by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_dataset1

        # When
        dataset = Dataset.by_id(test_dataset1['id'])

        # Then
        assert isinstance(dataset, pd.Series)
        assert isinstance(dataset, Dataset)
        assert dataset == test_dataset1

    @patch.object(VariableRepository, 'by_dataset')
    def test_get_variables(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        variables = test_dataset1.variables()

        # Then
        assert isinstance(variables, pd.DataFrame)
        assert isinstance(variables, Variables)
        assert variables == test_variables


class TestDatasets(unittest.TestCase):

    @patch.object(DatasetRepository, 'all')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = Datasets.all()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)

    @patch.object(DatasetRepository, 'by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_dataset1

        # When
        dataset = Datasets.by_id(test_dataset1['id'])

        # Then
        assert isinstance(dataset, pd.Series)
        assert isinstance(dataset, Dataset)
        assert dataset == test_dataset1
