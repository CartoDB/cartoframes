"""Unit tests for cartoframes.client.SQLClient"""
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
    
from cartoframes.client import SQLClient, internal

SQL_SELECT_RESPONSE = {
    'rows': [
        {
            'adm0name': 'Belize',
            'pop_max': 15220,
            'the_geom': '0101000020E610000048F259B9173156C091EB964485403140'
        }
    ],
    'time': 0.001,
    'fields': {
        'adm0name': {'type': 'string', 'pgtype': 'text'},
        'pop_max': {'type': 'number', 'pgtype': 'int4'},
        'the_geom': {'type': 'geometry', 'wkbtype': 'Unknown', 'dims': 2, 'srid': 4326}
    },
    'total_rows': 1
}


class MockClient():
    def __init__(self, response):
        self.response = response

    def execute_query(self, q):
        return self.response

    def execute_long_running_query(self, q):
        return self.response


class TestSQLClient(unittest.TestCase):
    def setUp(self):
        self._mock_client = MockClient('')
        internal.create_client = lambda c, s: self._mock_client
        self._sql_client = SQLClient(None)

    def test_query(self):
        """client.SQLClient.query"""
        self._mock_client.response = SQL_SELECT_RESPONSE

        output = self._sql_client.query('')
        self.assertEqual(output, [{
            'adm0name': 'Belize',
            'pop_max': 15220,
            'the_geom': '0101000020E610000048F259B9173156C091EB964485403140'
        }])

        output = self._sql_client.query('', verbose=True)
        self.assertEqual(output, SQL_SELECT_RESPONSE)
