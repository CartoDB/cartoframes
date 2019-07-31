"""Unit tests for cartoframes.client.SQLClient"""
import unittest

from cartoframes import context
from cartoframes.client import SQLClient
from cartoframes.auth import Credentials

from ..mocks.context_mock import ContextMock


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

SQL_SCHEMA_RESPONSE = {
    'rows': [],
    'time': 0.003,
    'fields': {
        'column_a': {'type': 'string', 'pgtype': 'text'},
        'column_b': {'type': 'number', 'pgtype': 'int4'},
        'column_c': {'type': 'geometry', 'wkbtype': 'Unknown', 'dims': 2, 'srid': 4326}
    },
    'total_rows': 0
}

SQL_DESCRIBE_STRING = {
    'rows': [
        {'count': 12345}
    ]
}

SQL_DESCRIBE_NUMBER = {
    'rows': [
        {'count': 12345, 'avg': 123.45, 'min': 0, 'max': 1000}
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


class MockContext():
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
        self._context_mock = ContextMock()
        # Mock create_context method
        self.original_create_context = context.create_context
        context.create_context = lambda c: self._context_mock
        credentials = Credentials('user_name', '1234567890')
        self._sql_client = SQLClient(credentials)

    def tearDown(self):
        context.create_context = self.original_create_context

    def test_query(self):
        """client.SQLClient.query"""
        self._context_mock.response = SQL_SELECT_RESPONSE
        output = self._sql_client.query('')

        self.assertEqual(output, [{
            'column_a': 'A',
            'column_b': 123,
            'column_c': '0123456789ABCDEF'
        }])

    def test_query_verbose(self):
        """client.SQLClient.query verbose"""
        self._context_mock.response = SQL_SELECT_RESPONSE
        output = self._sql_client.query('', verbose=True)

        self.assertEqual(output, SQL_SELECT_RESPONSE)

    def test_execute(self):
        """client.SQLClient.execute"""
        self._context_mock.response = SQL_BATCH_RESPONSE
        output = self._sql_client.execute('')

        self.assertEqual(output, SQL_BATCH_RESPONSE)

    def test_distinct(self):
        """client.SQLClient.distinct"""
        self._context_mock.response = SQL_DISTINCT_RESPONSE
        output = self._sql_client.distinct('table_name', 'column_name')

        self.assertEqual(self._context_mock.query.strip(), '''
            SELECT column_name, COUNT(*) FROM table_name
            GROUP BY 1 ORDER BY 2 DESC
        '''.strip())
        self.assertEqual(output, [('A', 1234), ('B', 5678)])

    def test_count(self):
        """client.SQLClient.count"""
        self._context_mock.response = SQL_COUNT_RESPONSE
        output = self._sql_client.count('table_name')

        self.assertEqual(self._context_mock.query.strip(), '''
            SELECT COUNT(*) FROM table_name;
        '''.strip())
        self.assertEqual(output, 12345)

    def test_bounds(self):
        """client.SQLClient.bounds"""
        self._context_mock.response = SQL_BOUNDS_RESPONSE
        output = self._sql_client.bounds('query')

        self.assertEqual(self._context_mock.query.strip(), '''
            SELECT ARRAY[
                ARRAY[st_xmin(geom_env), st_ymin(geom_env)],
                ARRAY[st_xmax(geom_env), st_ymax(geom_env)]
            ] bounds FROM (
                SELECT ST_Extent(the_geom) geom_env
                FROM (query) q
            ) q;
        '''.strip())
        self.assertEqual(output, [
            [-16.2500006525, 28.0999760122],
            [2.65424597028, 43.530016092]
        ])

    def test_schema(self):
        """client.SQLClient.schema"""
        self._context_mock.response = SQL_SCHEMA_RESPONSE
        output = self._sql_client.schema('table_name', raw=True)

        self.assertEqual(self._context_mock.query.strip(), '''
            SELECT * FROM table_name LIMIT 0;
        '''.strip())
        self.assertEqual(output, {
            'column_a': 'string',
            'column_b': 'number',
            'column_c': 'geometry'
        })

    def test_describe_type_string(self):
        """client.SQLClient.describe type: string"""
        self._sql_client._get_column_type = lambda t, c: 'string'
        self._context_mock.response = SQL_DESCRIBE_NUMBER
        self._sql_client.describe('table_name', 'column_name')

        self.assertEqual(self._context_mock.query.strip(), '''
            SELECT COUNT(*)
            FROM table_name;
        '''.strip())

    def test_describe_type_number(self):
        """client.SQLClient.describe type: number"""
        self._sql_client._get_column_type = lambda t, c: 'number'
        self._context_mock.response = SQL_DESCRIBE_NUMBER
        self._sql_client.describe('table_name', 'column_name')

        self.assertEqual(self._context_mock.query.strip(), '''
            SELECT COUNT(*),AVG(column_name),MIN(column_name),MAX(column_name)
            FROM table_name;
        '''.strip())

    def test_create_table_no_cartodbfy(self):
        """client.SQLClient.create_table"""
        self._sql_client.create_table(
            'table_name', [('id', 'INT'), ('name', 'TEXT')], cartodbfy=False)

        self.assertEqual(self._context_mock.query.strip(), '''
            BEGIN;
            DROP TABLE IF EXISTS table_name;
            CREATE TABLE table_name (id INT,name TEXT);
            ;
            COMMIT;
        '''.strip())

    def test_create_table_cartodbfy_org_user(self):
        """client.SQLClient.create_table cartodbfy: organization user"""
        self._sql_client._context.get_schema = lambda: 'user_name'
        self._sql_client.create_table(
            'table_name', [('id', 'INT'), ('name', 'TEXT')])

        self.assertEqual(self._context_mock.query.strip(), '''
            BEGIN;
            DROP TABLE IF EXISTS table_name;
            CREATE TABLE table_name (id INT,name TEXT);
            SELECT CDB_CartoDBFyTable('user_name', 'table_name');
            COMMIT;
        '''.strip())

    def test_create_table_cartodbfy_public_user(self):
        """client.SQLClient.create_table cartodbfy: public user"""
        self._sql_client.create_table(
            'table_name', [('id', 'INT'), ('name', 'TEXT')])

        self.assertEqual(self._context_mock.query.strip(), '''
            BEGIN;
            DROP TABLE IF EXISTS table_name;
            CREATE TABLE table_name (id INT,name TEXT);
            SELECT CDB_CartoDBFyTable('public', 'table_name');
            COMMIT;
        '''.strip())

    def test_insert_table(self):
        """client.SQLClient.insert_table"""
        self._sql_client.insert_table('table_name', ['id', 'name'], [0, 'a'])

        self.assertEqual(self._context_mock.query.strip(), '''
            INSERT INTO table_name (id,name) VALUES(0,'a');
        '''.strip())

    def test_update_table(self):
        """client.SQLClient.update_table"""
        self._sql_client.update_table('table_name', 'name', 'b', 'id = 0')

        self.assertEqual(self._context_mock.query.strip(), '''
            UPDATE table_name SET name='b' WHERE id = 0;
        '''.strip())

    def test_rename_table(self):
        """client.SQLClient.rename_table"""
        self._sql_client.rename_table('table_name', 'new_table_name')

        self.assertEqual(self._context_mock.query.strip(), '''
            ALTER TABLE table_name RENAME TO new_table_name;
        '''.strip())

    def test_drop_table(self):
        """client.SQLClient.drop_table"""
        self._sql_client.drop_table('table_name')

        self.assertEqual(self._context_mock.query.strip(), '''
            DROP TABLE IF EXISTS table_name;
        '''.strip())
