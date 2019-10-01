import unittest
import pandas as pd

from cartoframes.data.observatory.variable import Variable, Variables
from cartoframes.data.observatory.dataset import Datasets
from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository

from .examples import test_datasets, test_variable1, test_variables, db_variable1

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestVariable(unittest.TestCase):

    @patch.object(VariableRepository, 'get_by_id')
    def test_get_variable_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variable1

        # When
        variable = Variable.get(test_variable1.id)

        # Then
        assert isinstance(variable, object)
        assert isinstance(variable, Variable)
        assert variable == test_variable1

    @patch.object(DatasetRepository, 'get_by_variable')
    def test_get_datasets_by_variable(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_variable1.datasets()

        # Then
        assert isinstance(datasets, list)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets

    def test_variable_properties(self):
        # Given
        variable = Variable(db_variable1)

        # When
        variable_id = variable.id
        name = variable.name
        description = variable.description
        starred = variable.starred

        # Then
        assert variable_id == db_variable1['id']
        assert name == db_variable1['name']
        assert description == db_variable1['description']
        assert starred == db_variable1['starred']

    def test_variable_is_exported_as_series(self):
        # Given
        variable = test_variable1

        # When
        variable_series = variable.to_series()

        # Then
        assert isinstance(variable_series, pd.Series)
        assert variable_series['id'] == variable.id


class TestVariables(unittest.TestCase):

    @patch.object(VariableRepository, 'get_all')
    def test_get_all_variables(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        variables = Variables.get_all()

        # Then
        assert isinstance(variables, list)
        assert isinstance(variables, Variables)
        assert variables == test_variables

    @patch.object(VariableRepository, 'get_by_id')
    def test_get_variable_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variable1

        # When
        variable = Variables.get(test_variable1.id)

        # Then
        assert isinstance(variable, object)
        assert isinstance(variable, Variable)
        assert variable == test_variable1

    # @patch.object(VariableRepository, 'get_all')
    # def test_variables_are_indexed_with_id(self, mocked_repo):
    #     # Given
    #     mocked_repo.return_value = test_variables
    #     variable_id = db_variable1['id']
    #
    #     # When
    #     variables = Variables.get_all()
    #     variable = variables.loc[variable_id]
    #
    #     # Then
    #     assert variable == test_variable1

    def test_variables_items_are_obtained_as_variable(self):
        # Given
        variables = test_variables

        # When
        variable = variables[0]

        # Then
        assert isinstance(variable, Variable)
        assert variable == test_variable1

    def test_variables_are_exported_as_dataframe(self):
        # Given
        variables = test_variables
        variable = variables[0]

        # When
        variable_df = variables.to_dataframe()
        sliced_variable = variable_df.iloc[0]

        # Then
        assert isinstance(variable_df, pd.DataFrame)
        assert isinstance(sliced_variable, pd.Series)
        assert sliced_variable.equals(variable.to_series())
