import unittest
import os
import json

from google.auth.exceptions import RefreshError

from carto.exceptions import CartoException

from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient
from google.cloud import bigquery

_WORKING_PROJECT = 'carto-do-customers'


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
        def query_raiser(self, query, **kwargs):
            raise RefreshError()
        original_query_method = BigQueryClient.query
        bigquery.Client.query = query_raiser

        bq_client = BigQueryClient(_WORKING_PROJECT, self.credentials)
        with self.assertRaises(CartoException):
            bq_client.query('select * from')

        bigquery.Client.query = original_query_method
