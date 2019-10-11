import unittest

from cartoframes.data.clients import SQLClient
from cartoframes.data.observatory.repository.repo_client import RepoClient

from ..examples import db_dataset1, db_dataset2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestRepoClient(unittest.TestCase):

    @patch.object(SQLClient, 'query')
    def test_run_query_with_one_filter(self, mocked_client):
        # Given
        mocked_client.return_value = [db_dataset1, db_dataset2]
        repo = RepoClient()
        query = 'SELECT t.* FROM datasets t'
        filters = {'category_id': 'demographics'}
        expected_query = "SELECT t.* FROM datasets t WHERE t.category_id = 'demographics'"

        # When
        categories = repo._run_query(query, filters)

        # Then
        mocked_client.assert_called_once_with(expected_query)
        assert categories == [db_dataset1, db_dataset2]

    @patch.object(SQLClient, 'query')
    def test_run_query_with_multiple_filter(self, mocked_client):
        # Given
        mocked_client.return_value = [db_dataset1, db_dataset2]
        repo = RepoClient()
        query = 'SELECT t.* FROM datasets t'
        filters = {
            'category_id': 'demographics',
            'country_id': 'usa'}
        expected_query = "SELECT t.* FROM datasets t WHERE t.category_id = 'demographics' AND t.country_id = 'usa'"

        # When
        datasets = repo._run_query(query, filters)

        # Then
        mocked_client.assert_called_once_with(expected_query)
        assert datasets == [db_dataset1, db_dataset2]

    @patch.object(SQLClient, 'query')
    def test_run_query_with_id_list(self, mocked_client):
        # Given
        mocked_client.return_value = [db_dataset1, db_dataset2]
        repo = RepoClient()
        query = 'SELECT t.* FROM datasets t'
        filters = {'id': ['carto-do.dataset.census', 'carto-do.dataset.municipalities']}
        expected_query = "SELECT t.* FROM datasets t " \
                         "WHERE t.id IN ('carto-do.dataset.census','carto-do.dataset.municipalities')"

        # When
        datasets = repo._run_query(query, filters)

        # Then
        mocked_client.assert_called_once_with(expected_query)
        assert datasets == [db_dataset1, db_dataset2]
