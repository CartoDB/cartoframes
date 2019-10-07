import pytest

from cartoframes.data.observatory.repository.repo_client import RepoClient
from cartoframes.data.observatory.repository.variable_group_repo import \
    VariableGroupRepository
from cartoframes.exceptions import DiscoveryException

from ..examples import (db_variable_group1, db_variable_group2,
                        test_variable_group1, test_variables_groups)

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestVariableGroupRepo():

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        repo = VariableGroupRepository()

        # When
        variables_groups = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with()
        assert variables_groups == test_variables_groups

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []

        # When
        repo = VariableGroupRepository()
        variables_groups = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with()
        assert variables_groups is None

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        requested_id = test_variable_group1['id']

        # When
        repo = VariableGroupRepository()
        variable_group = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with('id', requested_id)
        assert variable_group == test_variable_group1

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = VariableGroupRepository()

        # Then
        with pytest.raises(DiscoveryException):
            repo.get_by_id(requested_id)

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_dataset(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        dataset_id = 'dataset1'
        repo = VariableGroupRepository()

        # When
        variables_groups = repo.get_by_dataset(dataset_id)

        # Then
        mocked_repo.assert_called_once_with('dataset_id', dataset_id)
        assert variables_groups == test_variables_groups
