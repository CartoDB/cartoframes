"""Unit tests for cartoframes.client.SQLClient"""

from cartoframes.auth import Credentials
from cartoframes.data.clients import SQLClient
from tests.unit.mocks import mock_create_context

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


def sql_client(mocker, response=''):
    context_mock = mock_create_context(mocker, response)
    credentials = Credentials('user_name', '1234567890')
    return SQLClient(credentials), context_mock


class TestSQLClient(object):
    def test_query(self, mocker):
        """client.SQLClient.query"""
        client, _ = sql_client(mocker, SQL_SELECT_RESPONSE)
        output = client.query('')

        assert output == [{
            'column_a': 'A',
            'column_b': 123,
            'column_c': '0123456789ABCDEF'
        }]

    def test_query_verbose(self, mocker):
        """client.SQLClient.query verbose"""
        client, _ = sql_client(mocker, SQL_SELECT_RESPONSE)
        output = client.query('', verbose=True)

        assert output == SQL_SELECT_RESPONSE

    def test_execute(self, mocker):
        """client.SQLClient.execute"""
        client, _ = sql_client(mocker, SQL_BATCH_RESPONSE)
        output = client.execute('')

        assert output == SQL_BATCH_RESPONSE

    def test_distinct(self, mocker):
        """client.SQLClient.distinct"""
        client, context_mock = sql_client(mocker, SQL_DISTINCT_RESPONSE)
        output = client.distinct('table_name', 'column_name')

        assert context_mock.query.strip() == '''
            SELECT column_name, COUNT(*) FROM table_name
            GROUP BY 1 ORDER BY 2 DESC
        '''.strip()
        assert output == [('A', 1234), ('B', 5678)]

    def test_count(self, mocker):
        """client.SQLClient.count"""
        client, context_mock = sql_client(mocker, SQL_COUNT_RESPONSE)
        output = client.count('table_name')

        assert context_mock.query.strip() == '''
            SELECT COUNT(*) FROM table_name;
        '''.strip()
        assert output == 12345

    def test_bounds(self, mocker):
        """client.SQLClient.bounds"""
        client, context_mock = sql_client(mocker, SQL_BOUNDS_RESPONSE)
        output = client.bounds('query')

        assert context_mock.query.strip() == '''
            SELECT ARRAY[
                ARRAY[st_xmin(geom_env), st_ymin(geom_env)],
                ARRAY[st_xmax(geom_env), st_ymax(geom_env)]
            ] bounds FROM (
                SELECT ST_Extent(the_geom) geom_env
                FROM (query) q
            ) q;
        '''.strip()
        assert output == [
            [-16.2500006525, 28.0999760122],
            [2.65424597028, 43.530016092]
        ]

    def test_schema(self, mocker):
        """client.SQLClient.schema"""
        client, context_mock = sql_client(mocker, SQL_SCHEMA_RESPONSE)
        output = client.schema('table_name', raw=True)

        assert context_mock.query.strip() == '''
            SELECT * FROM table_name LIMIT 0;
        '''.strip()
        assert output == {
            'column_a': 'string',
            'column_b': 'number',
            'column_c': 'geometry'
        }

    def test_describe_type_string(self, mocker):
        """client.SQLClient.describe type: string"""
        client, context_mock = sql_client(mocker, SQL_DESCRIBE_NUMBER)
        client._get_column_type = lambda t, c: 'string'
        client.describe('table_name', 'column_name')

        assert context_mock.query.strip() == '''
            SELECT COUNT(*)
            FROM table_name;
        '''.strip()

    def test_describe_type_number(self, mocker):
        """client.SQLClient.describe type: number"""
        client, context_mock = sql_client(mocker, SQL_DESCRIBE_NUMBER)
        client._get_column_type = lambda t, c: 'number'
        client.describe('table_name', 'column_name')

        assert context_mock.query.strip() == '''
            SELECT COUNT(*),AVG(column_name),MIN(column_name),MAX(column_name)
            FROM table_name;
        '''.strip()

    def test_create_table_no_cartodbfy(self, mocker):
        """client.SQLClient.create_table"""
        client, context_mock = sql_client(mocker)
        client.create_table(
            'table_name', [('id', 'INT'), ('name', 'TEXT')], cartodbfy=False)

        assert context_mock.query.strip() == '''
            BEGIN;
            DROP TABLE IF EXISTS table_name;
            CREATE TABLE table_name (id INT,name TEXT);
            ;
            COMMIT;
        '''.strip()

    def test_create_table_cartodbfy_org_user(self, mocker):
        """client.SQLClient.create_table cartodbfy: organization user"""
        client, context_mock = sql_client(mocker)
        client._context.get_schema = lambda: 'user_name'
        client.create_table(
            'table_name', [('id', 'INT'), ('name', 'TEXT')])

        assert context_mock.query.strip() == '''
            BEGIN;
            DROP TABLE IF EXISTS table_name;
            CREATE TABLE table_name (id INT,name TEXT);
            SELECT CDB_CartoDBFyTable('user_name', 'table_name');
            COMMIT;
        '''.strip()

    def test_create_table_cartodbfy_public_user(self, mocker):
        """client.SQLClient.create_table cartodbfy: public user"""
        client, context_mock = sql_client(mocker)
        client.create_table(
            'table_name', [('id', 'INT'), ('name', 'TEXT')])

        assert context_mock.query.strip() == '''
            BEGIN;
            DROP TABLE IF EXISTS table_name;
            CREATE TABLE table_name (id INT,name TEXT);
            SELECT CDB_CartoDBFyTable('public', 'table_name');
            COMMIT;
        '''.strip()

    def test_insert_table(self, mocker):
        """client.SQLClient.insert_table"""
        client, context_mock = sql_client(mocker)
        client.insert_table('table_name', ['id', 'name'], [0, 'a'])

        assert context_mock.query.strip() == '''
            INSERT INTO table_name (id,name) VALUES(0,'a');
        '''.strip()

    def test_update_table(self, mocker):
        """client.SQLClient.update_table"""
        client, context_mock = sql_client(mocker)
        client.update_table('table_name', 'name', 'b', 'id = 0')

        assert context_mock.query.strip() == '''
            UPDATE table_name SET name='b' WHERE id = 0;
        '''.strip()

    def test_rename_table(self, mocker):
        """client.SQLClient.rename_table"""
        client, context_mock = sql_client(mocker)
        client.rename_table('table_name', 'new_table_name')

        assert context_mock.query.strip() == '''
            ALTER TABLE table_name RENAME TO new_table_name;
        '''.strip()

    def test_drop_table(self, mocker):
        """client.SQLClient.drop_table"""
        client, context_mock = sql_client(mocker)
        client.drop_table('table_name')

        assert context_mock.query.strip() == '''
            DROP TABLE IF EXISTS table_name;
        '''.strip()
