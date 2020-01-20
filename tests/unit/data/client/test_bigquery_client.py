import os
import csv
import pandas as pd

from unittest.mock import Mock, patch

from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient


class ResponseMock(list):
    def __init__(self, data, **kwargs):
        super(ResponseMock, self).__init__(data, **kwargs)
        self.total_rows = len(data)


class QueryJobMock(object):
    def __init__(self, response):
        self.response = response

    def result(self):
        return ResponseMock(self.response)


class TestBigQueryClient(object):
    def setup_method(self):
        self.original_init_clients = BigQueryClient._init_clients
        BigQueryClient._init_clients = Mock(return_value=(True, True, True))
        self.username = 'username'
        self.apikey = 'apikey'
        self.credentials = Credentials(self.username, self.apikey)
        self.file_path = '/tmp/test_download.csv'

    def teardown_method(self):
        self.credentials = None
        BigQueryClient._init_clients = self.original_init_clients

        if os.path.isfile(self.file_path):
            os.remove(self.file_path)

    @patch.object(BigQueryClient, 'get_table_column_names')
    @patch.object(BigQueryClient, '_download_by_bq_storage_api')
    def test_download_to_file_full(self, download_mock, column_names_mock):
        data = [{'0': 'word', '1': 'word word'}]
        columns = ['column1', 'column2']

        column_names_mock.return_value = Mock(return_value=columns)
        download_mock.return_value = data

        file_path = self.file_path

        bq_client = BigQueryClient(self.credentials)
        job = QueryJobMock(data)
        bq_client.download_to_file(job, file_path, column_names=columns, progress_bar=False)

        rows = []
        with open(file_path) as csvfile:
            csvreader = csv.reader(csvfile)
            rows.append(next(csvreader))
            rows.append(next(csvreader))

        assert rows[0] == columns
        assert rows[1] == list(data[0].values())

    @patch.object(BigQueryClient, 'get_table_column_names')
    @patch.object(BigQueryClient, '_download_by_bq_storage_api')
    def test_download_to_dataframe_full(self, download_mock, column_names_mock):
        data = [{'column1': 'word', 'column2': 'word word'}]
        columns = ['column1', 'column2']

        column_names_mock.return_value = Mock(return_value=columns)
        download_mock.return_value = data

        expected_df = pd.DataFrame(data, columns=columns)

        bq_client = BigQueryClient(self.credentials)
        job = QueryJobMock(data)
        df = bq_client.download_to_dataframe(job)

        assert df.equals(expected_df)
