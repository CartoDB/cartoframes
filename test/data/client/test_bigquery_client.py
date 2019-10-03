import unittest
import os
import json

from google.auth.exceptions import RefreshError

from carto.exceptions import CartoException

from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient, _download_query
from google.cloud import bigquery

_WORKING_PROJECT = 'carto-do-customers'


class RefreshTokenChecker(object):
    def __init__(self, response, raise_after=1):
        self.number_of_calls = 0
        self.response = response
        self.raise_after = raise_after

    def query_raiser(self, query, **kwargs):
        self.number_of_calls += 1
        if self.number_of_calls > self.raise_after:
            return self.response
        else:
            raise RefreshError()


class TestBigQueryClient(unittest.TestCase):
    def setUp(self):
        if (os.environ.get('APIKEY') is None or os.environ.get('USERNAME') is None):
            creds = json.loads(open('test/secret.json').read())
            self.apikey = creds['APIKEY']
            self.username = creds['USERNAME']
        else:
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']

        self.credentials = Credentials(self.username, self.apikey)

    def test_instantiation(self):
        bq_client = BigQueryClient(_WORKING_PROJECT, self.credentials)
        self.assertIsInstance(bq_client, BigQueryClient)

    def test_refresh_token_raises_cartoexception(self):
        refresh_token_checker = RefreshTokenChecker('', 10)
        original_query_method = BigQueryClient.query
        bigquery.Client.query = refresh_token_checker.query_raiser

        bq_client = BigQueryClient(_WORKING_PROJECT, self.credentials)
        with self.assertRaises(CartoException):
            bq_client.query('select * from')

        bigquery.Client.query = original_query_method

    def test_refresh_token(self):
        expected_response = 'ok'
        refresh_token_checker = RefreshTokenChecker(expected_response, 1)
        original_query_method = BigQueryClient.query
        bigquery.Client.query = refresh_token_checker.query_raiser

        bq_client = BigQueryClient(_WORKING_PROJECT, self.credentials)
        response = bq_client.query('select * from')
        self.assertEqual(response, expected_response)

        bigquery.Client.query = original_query_method

    def test_download_query_simple(self):
        project = 'fake_project'
        dataset = 'fake_dataset'
        table = 'fake_table'
        limit = None
        offset = None
        expected_query = 'SELECT * FROM `{}.{}.{}`'.format(project, dataset, table)

        query = _download_query(project, dataset, table, limit, offset)

        self.assertEqual(query, expected_query)

    def test_download_query_limit(self):
        project = 'fake_project'
        dataset = 'fake_dataset'
        table = 'fake_table'
        limit = 10
        offset = None
        expected_query = 'SELECT * FROM `{}.{}.{}` LIMIT {}'.format(project, dataset, table, limit)

        query = _download_query(project, dataset, table, limit, offset)

        self.assertEqual(query, expected_query)

    def test_download_query_offset(self):
        project = 'fake_project'
        dataset = 'fake_dataset'
        table = 'fake_table'
        limit = None
        offset = 10
        expected_query = 'SELECT * FROM `{}.{}.{}` OFFSET {}'.format(project, dataset, table, offset)

        query = _download_query(project, dataset, table, limit, offset)

        self.assertEqual(query, expected_query)

    def test_download_query_limit_offset(self):
        project = 'fake_project'
        dataset = 'fake_dataset'
        table = 'fake_table'
        limit = 10
        offset = 20
        expected_query = 'SELECT * FROM `{}.{}.{}` LIMIT {} OFFSET {}'.format(project, dataset, table, limit, offset)

        query = _download_query(project, dataset, table, limit, offset)

        self.assertEqual(query, expected_query)

