import unittest
import pandas as pd

from cartoframes.data.observatory.variable_group import VariableGroup, VariablesGroups
from cartoframes.data.observatory.variable import Variables
from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.variable_group_repo import VariableGroupRepository
from cartoframes.exceptions import DiscoveryException

from .examples import test_variables_groups, test_variable_group1, test_variables, db_variable_group1

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestVariableGroup(unittest.TestCase):

    @patch.object(VariableGroupRepository, 'get_by_id')
    def test_get_variable_group_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variable_group1

        # When
        variable_group = VariableGroup.get_by_id(test_variable_group1['id'])

        # Then
        assert isinstance(variable_group, pd.Series)
        assert isinstance(variable_group, VariableGroup)
        assert variable_group == test_variable_group1

    @patch.object(VariableRepository, 'get_by_variable_group')
    def test_get_variables_by_variable_group(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        variables = test_variable_group1.variables()

        # Then
        assert isinstance(variables, pd.DataFrame)
        assert isinstance(variables, Variables)
        assert variables == test_variables

    def test_get_variables_by_variable_group_fails_if_column_Series(self):
        # Given
        variable_group = test_variables_groups.id

        # Then
        with self.assertRaises(DiscoveryException):
            variable_group.variables()


class TestVariablesGroups(unittest.TestCase):

    @patch.object(VariableGroupRepository, 'get_all')
    def test_get_all_variables_groups(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables_groups

        # When
        variables_groups = VariablesGroups.get_all()

        # Then
        assert isinstance(variables_groups, pd.DataFrame)
        assert isinstance(variables_groups, VariablesGroups)
        assert variables_groups == test_variables_groups

    @patch.object(VariableGroupRepository, 'get_by_id')
    def test_get_variable_group_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variable_group1

        # When
        variable_group = VariablesGroups.get_by_id(test_variable_group1['id'])

        # Then
        assert isinstance(variable_group, pd.Series)
        assert isinstance(variable_group, VariableGroup)
        assert variable_group == test_variable_group1

    @patch.object(VariableGroupRepository, 'get_all')
    def test_variables_groups_are_indexed_with_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables_groups
        variable_group_id = db_variable_group1['id']

        # When
        variables_groups = VariablesGroups.get_all()
        variable_group = variables_groups.loc[variable_group_id]

        # Then
        assert variable_group == test_variable_group1

    @patch.object(VariableGroupRepository, 'get_all')
    def test_variables_groups_slice_is_variable_group_and_series(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables_groups

        # When
        variables_groups = VariablesGroups.get_all()
        variable_group = variables_groups.iloc[0]

        # Then
        assert isinstance(variable_group, VariableGroup)
        assert isinstance(variable_group, pd.Series)
