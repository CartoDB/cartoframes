import os
import json
import pytest
import unittest

from google.auth.exceptions import RefreshError
from google.cloud import bigquery

from cartoframes.auth import Credentials
from cartoframes.exceptions import DOError
from cartoframes.data.clients.bigquery_client import BigQueryClient


_WORKING_PROJECT = 'carto-do-customers'


class RefreshTokenChecker(object):
    def __init__(self, response, raise_after=1):
        self.number_of_calls = 0
        self.response = response
        self.raise_after = raise_after

    def query_raiser(self, query, **kwargs):
        self.number_of_calls += 1
        if self.number_of_calls < self.raise_after:
            return self.response
        else:
            raise RefreshError()


class ResponseMock(list):
    def __init__(self, data, **kwargs):
        super(ResponseMock, self).__init__(data, **kwargs)
        self.total_rows = len(data)


class QueryJobMock(object):
    def __init__(self, response):
        self.response = response

    def result(self):
        return ResponseMock(self.response)


class TestBigQueryClient(unittest.TestCase):
    def setUp(self):
        if (os.environ.get('APIKEY') is None or os.environ.get('USERNAME') is None):
            creds = json.loads(open('tests/e2e/secret.json').read())
            self.apikey = creds['APIKEY']
            self.username = creds['USERNAME']
        else:
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']

        self.credentials = Credentials(self.username, self.apikey)
        self.file_path = '/tmp/test_download.csv'

    def tearDown(self):
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)

    def test_instantiation(self):
        bq_client = BigQueryClient(self.credentials)
        assert isinstance(bq_client, BigQueryClient)

    def test_refresh_token_raises_cartoexception(self):
        refresh_token_checker = RefreshTokenChecker('', 0)
        original_query_method = bigquery.Client.query
        bigquery.Client.query = refresh_token_checker.query_raiser

        bq_client = BigQueryClient(self.credentials)
        with pytest.raises(DOError):
            bq_client.query('select * from')

        bigquery.Client.query = original_query_method

    def test_refresh_token(self):
        expected_response = 'ok'
        refresh_token_checker = RefreshTokenChecker(expected_response, 2)
        original_query_method = bigquery.Client.query
        bigquery.Client.query = refresh_token_checker.query_raiser

        bq_client = BigQueryClient(self.credentials)
        response = bq_client.query('select * from')
        assert response == expected_response

        bigquery.Client.query = original_query_method

    def test_download_using_if_exists(self):
        project = _WORKING_PROJECT
        dataset = 'fake_dataset'
        table = 'fake_table'
        file_path = self.file_path

        bq_client = BigQueryClient(self.credentials)

        query = 'SELECT * FROM `{}.{}.{}`'.format(project, dataset, table)
        job = bq_client.query(query)

        with open(file_path, 'w'):
            with self.assertRaises(OSError):
                bq_client.download_to_file(job, file_path, fail_if_exists=True, progress_bar=False)
