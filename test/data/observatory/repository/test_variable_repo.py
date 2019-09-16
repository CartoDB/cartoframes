import unittest

from cartoframes.exceptions import DiscoveryException

from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_variable1, test_variables, db_variable1, db_variable2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestVariableRepo(unittest.TestCase):

    @patch.object(RepoClient, 'get_variables')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable1, db_variable2]
        repo = VariableRepository()

        # When
        variables = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with()
        assert variables == test_variables

    @patch.object(RepoClient, 'get_variables')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []

        # When
        repo = VariableRepository()
        variables = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with()
        assert variables is None

    @patch.object(RepoClient, 'get_variables')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable1, db_variable2]
        requested_id = test_variable1['id']

        # When
        repo = VariableRepository()
        variable = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with('id', requested_id)
        assert variable == test_variable1

    @patch.object(RepoClient, 'get_variables')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = VariableRepository()

        # Then
        with self.assertRaises(DiscoveryException):
            repo.get_by_id(requested_id)
