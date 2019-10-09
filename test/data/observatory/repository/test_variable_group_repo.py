import unittest

from cartoframes.exceptions import DiscoveryException
from cartoframes.data.observatory.entity import CatalogList
from cartoframes.data.observatory.variable_group import VariableGroup
from cartoframes.data.observatory.repository.variable_group_repo import VariableGroupRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_variable_group1, test_variables_groups, db_variable_group1, db_variable_group2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestVariableGroupRepo(unittest.TestCase):

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        repo = VariableGroupRepository()

        # When
        variables_groups = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert isinstance(variables_groups, CatalogList)
        assert variables_groups == test_variables_groups

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []

        # When
        repo = VariableGroupRepository()
        variables_groups = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None)
        assert variables_groups is None

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable_group1, db_variable_group2]
        requested_id = db_variable_group1['id']

        # When
        repo = VariableGroupRepository()
        variable_group = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with({'id': requested_id})
        assert isinstance(variable_group, VariableGroup)
        assert variable_group == test_variable_group1

    @patch.object(RepoClient, 'get_variables_groups')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = VariableGroupRepository()

        # Then
        with self.assertRaises(DiscoveryException):
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
        mocked_repo.assert_called_once_with({'dataset_id': dataset_id})
        assert isinstance(variables_groups, CatalogList)
        assert variables_groups == test_variables_groups

    @patch.object(RepoClient, 'get_variables_groups')
    def test_missing_fields_are_mapped_as_None(self, mocked_repo):
        # Given
        mocked_repo.return_value = [{'id': 'variable_group1'}]
        repo = VariableGroupRepository()

        expected_variables_groups = CatalogList([VariableGroup({
            'id': 'variable_group1',
            'name': None,
            'dataset_id': None,
            'starred': None
        })])

        # When
        variables_groups = repo.get_all()

        # Then
        assert variables_groups == expected_variables_groups
