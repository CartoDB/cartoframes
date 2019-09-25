import unittest
import os
import json

from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient

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
