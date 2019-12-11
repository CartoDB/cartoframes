import os
import csv
import json
import pytest
import unittest

from carto.exceptions import CartoException
from google.auth.exceptions import RefreshError
from google.cloud import bigquery

from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

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
        bq_client = BigQueryClient(_WORKING_PROJECT, self.credentials)
        assert isinstance(bq_client, BigQueryClient)

    def test_refresh_token_raises_cartoexception(self):
        refresh_token_checker = RefreshTokenChecker('', 10)
        original_query_method = BigQueryClient.query
        bigquery.Client.query = refresh_token_checker.query_raiser

        bq_client = BigQueryClient(_WORKING_PROJECT, self.credentials)
        with pytest.raises(CartoException):
            bq_client.query('select * from')

        bigquery.Client.query = original_query_method

    def test_refresh_token(self):
        expected_response = 'ok'
        refresh_token_checker = RefreshTokenChecker(expected_response, 1)
        original_query_method = BigQueryClient.query
        bigquery.Client.query = refresh_token_checker.query_raiser

        bq_client = BigQueryClient(_WORKING_PROJECT, self.credentials)
        response = bq_client.query('select * from')
        assert response == expected_response

        bigquery.Client.query = original_query_method

    def test_download_full(self):
        data = [{'0': 'word', '1': 'word word'}]
        columns = ['column1', 'column2']

        original_query = BigQueryClient.query
        BigQueryClient.query = Mock(return_value=QueryJobMock(data))
        original_get_table_column_names = BigQueryClient.get_table_column_names
        BigQueryClient.get_table_column_names = Mock(return_value=columns)

        project = _WORKING_PROJECT
        dataset = 'fake_dataset'
        table = 'fake_table'
        file_path = self.file_path

        bq_client = BigQueryClient(project, self.credentials)

        query = 'SELECT * FROM `{}.{}.{}`'.format(project, dataset, table)
        job = bq_client.query(query)
        file_path = bq_client.download_to_file(job, file_path=file_path, column_names=columns, progress_bar=False)

        self.assertTrue(os.path.isfile(file_path))

        rows = []
        with open(file_path) as csvfile:
            csvreader = csv.reader(csvfile)
            rows.append(next(csvreader))
            rows.append(next(csvreader))

        self.assertEqual(rows[0], columns)
        self.assertEqual(rows[1], list(data[0].values()))

        BigQueryClient.query = original_query
        BigQueryClient.get_table_column_names = original_get_table_column_names

    def test_download_using_if_exists(self):
        project = _WORKING_PROJECT
        dataset = 'fake_dataset'
        table = 'fake_table'
        file_path = self.file_path

        bq_client = BigQueryClient(project, self.credentials)

        query = 'SELECT * FROM `{}.{}.{}`'.format(project, dataset, table)
        job = bq_client.query(query)

        with open(file_path, 'w'):
            with self.assertRaises(CartoException):
                bq_client.download_to_file(job, file_path=file_path,
                                           fail_if_exists=True, progress_bar=False)
