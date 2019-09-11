import unittest
import pandas as pd

from cartoframes.data.observatory.variable import Variable, Variables
from cartoframes.data.observatory.dataset import Datasets
from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository

from .examples import test_datasets, test_variable1, test_variables

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestVariable(unittest.TestCase):

    @patch.object(VariableRepository, 'get_by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variable1

        # When
        variable = Variable.get_by_id(test_variable1['id'])

        # Then
        assert isinstance(variable, pd.Series)
        assert isinstance(variable, Variable)
        assert variable == test_variable1

    @patch.object(DatasetRepository, 'get_by_variable')
    def test_get_datasets(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_variable1.datasets()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets


class TestVariables(unittest.TestCase):

    @patch.object(VariableRepository, 'get_all')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        countries = Variables.all()

        # Then
        assert isinstance(countries, pd.DataFrame)
        assert isinstance(countries, Variables)
        assert countries == test_variables

    @patch.object(VariableRepository, 'get_by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variable1

        # When
        variable = Variables.get_by_id(test_variable1['id'])

        # Then
        assert isinstance(variable, pd.Series)
        assert isinstance(variable, Variable)
        assert variable == test_variable1
