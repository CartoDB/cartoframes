"""Unit tests for cartoframes.client.SQLClient"""
import unittest
    
from cartoframes.client import SQLClient, internal

SQL_SELECT_RESPONSE = {
    'rows': [{
        'column_a': 'A',
        'column_b': 123,
        'column_c': '0123456789ABCDEF'
    }],
    'time': 0.001,
    'fields': {
        'column_a': {'type': 'string', 'pgtype': 'text'},
        'column_b': {'type': 'number', 'pgtype': 'int4'},
        'column_c': {'type': 'geometry', 'wkbtype': 'Unknown', 'dims': 2, 'srid': 4326}
    },
    'total_rows': 1
}

SQL_DISTINCT_RESPONSE = {
    'rows': [
        {'column_name': 'A', 'count': 1234},
        {'column_name': 'B', 'count': 5678}
    ]
}

SQL_COUNT_RESPONSE = {
    'rows': [
        {'count': 12345}
    ]
}

SQL_BOUNDS_RESPONSE = {
    'rows': [
        {'bounds': [[-16.2500006525, 28.0999760122], [2.65424597028, 43.530016092]]}
    ]
}

SQL_BATCH_RESPONSE = {
    'user': 'username',
    'status': 'done',
    'query': 'SELECT * FROM table_name',
    'created_at': '2019-07-12T09:07:16.648Z',
    'updated_at': '2019-07-12T09:07:16.786Z',
    'job_id': 'bd07b045-262f-432e-a7a1-82dba2cbbbb4'
}


class MockClient():
    def __init__(self):
        self.query = ''
        self.response = ''

    def execute_query(self, q):
        self.query = q
        return self.response

    def execute_long_running_query(self, q):
        self.query = q
        return self.response


class TestSQLClient(unittest.TestCase):
    def setUp(self):
        self._mock_client = MockClient()
        # Mock create_client method
        internal.create_client = lambda c, s: self._mock_client
        self._sql_client = SQLClient(None)

    def test_query(self):
        """client.SQLClient.query"""
        self._mock_client.response = SQL_SELECT_RESPONSE
        output = self._sql_client.query('')

        self.assertEqual(output, [{
            'column_a': 'A',
            'column_b': 123,
            'column_c': '0123456789ABCDEF'
        }])

    def test_query_verbose(self):
        """client.SQLClient.query verbose"""
        self._mock_client.response = SQL_SELECT_RESPONSE
        output = self._sql_client.query('', verbose=True)

        self.assertEqual(output, SQL_SELECT_RESPONSE)

    def test_execute(self):
        """client.SQLClient.execute"""
        self._mock_client.response = SQL_BATCH_RESPONSE
        output = self._sql_client.execute('')

        self.assertEqual(output, SQL_BATCH_RESPONSE)

    def test_distinct(self):
        """client.SQLClient.distinct"""
        self._mock_client.response = SQL_DISTINCT_RESPONSE
        output = self._sql_client.distinct('table_name', 'column_name')

        self.assertEqual(self._mock_client.query, '''
            SELECT column_name, COUNT(*) FROM table_name
            GROUP BY 1 ORDER BY 2 DESC
        '''.strip())
        self.assertEqual(output, [('A', 1234), ('B', 5678)])

    def test_count(self):
        """client.SQLClient.count"""
        self._mock_client.response = SQL_COUNT_RESPONSE
        output = self._sql_client.count('table_name')

        self.assertEqual(self._mock_client.query, '''
            SELECT COUNT(*) FROM table_name;
        '''.strip())
        self.assertEqual(output, 12345)

    def test_bounds(self):
        """client.SQLClient.bounds"""
        self._mock_client.response = SQL_BOUNDS_RESPONSE
        output = self._sql_client.bounds('query')

        self.assertEqual(self._mock_client.query, '''
            SELECT ARRAY[
                ARRAY[st_xmin(geom_env), st_ymin(geom_env)],
                ARRAY[st_xmax(geom_env), st_ymax(geom_env)]
            ] bounds FROM (
                SELECT ST_Extent(the_geom) geom_env
                FROM (query) q
            ) q;
        '''.strip())
        self.assertEqual(output, [[-16.2500006525, 28.0999760122], [2.65424597028, 43.530016092]])
