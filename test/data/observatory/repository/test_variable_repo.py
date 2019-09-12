import unittest

from cartoframes.data.observatory.variable import Variables

from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_variable1, test_variables, db_variable1, db_variable2

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestVariableRepo(unittest.TestCase):

    def setUp(self):
        RepoClient.get_variables = Mock(return_value=[db_variable1, db_variable2])

    def test_get_all(self):
        # Given
        repo = VariableRepository()

        # When
        variables = repo.all()

        # Then
        assert variables == test_variables

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_variables = Mock(return_value=[])

        # When
        repo = VariableRepository()
        variables = repo.all()

        # Then
        assert variables == Variables([])

    def test_get_by_id(self):
        # Given
        requested_id = test_variable1['id']

        # When
        repo = VariableRepository()
        variable = repo.by_id(requested_id)

        # Then
        assert variable == test_variable1

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_variables = Mock(return_value=[])
        requested_id = 'unknown_id'

        # When
        repo = VariableRepository()
        variable = repo.by_id(requested_id)

        # Then
        assert variable is None
