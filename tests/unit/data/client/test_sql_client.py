"""Unit tests for cartoframes.client.SQLClient"""

from collections import OrderedDict

from cartoframes.auth import Credentials
from cartoframes.io.managers.context_manager import ContextManager
from cartoframes.data.clients import SQLClient

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


class TestSQLClient(object):

    def setup_method(self):
        self.credentials = Credentials('user_name', '1234567890')

    def test_query(self, mocker):
        """client.SQLClient.query"""
        mock = mocker.patch.object(ContextManager, 'execute_query', return_value=SQL_SELECT_RESPONSE)
        output = SQLClient(self.credentials).query('query')

        assert output == [{
            'column_a': 'A',
            'column_b': 123,
            'column_c': '0123456789ABCDEF'
        }]
        mock.assert_called_once_with('query')

    def test_query_verbose(self, mocker):
        """client.SQLClient.query verbose"""
        mock = mocker.patch.object(ContextManager, 'execute_query', return_value=SQL_SELECT_RESPONSE)
        output = SQLClient(self.credentials).query('query', verbose=True)

        assert output == SQL_SELECT_RESPONSE
        mock.assert_called_once_with('query')

    def test_execute(self, mocker):
        """client.SQLClient.execute"""
        mock = mocker.patch.object(ContextManager, 'execute_long_running_query', return_value=SQL_BATCH_RESPONSE)
        output = SQLClient(self.credentials).execute('query')

        assert output == SQL_BATCH_RESPONSE
        mock.assert_called_once_with('query')

    def test_distinct(self, mocker):
        """client.SQLClient.distinct"""
        mock = mocker.patch.object(ContextManager, 'execute_query', return_value=SQL_DISTINCT_RESPONSE)
        output = SQLClient(self.credentials).distinct('table_name', 'column_name')

        assert output == [('A', 1234), ('B', 5678)]
        mock.assert_called_once_with('''
            SELECT column_name, COUNT(*) FROM table_name
            GROUP BY 1 ORDER BY 2 DESC
        '''.strip())

    def test_count(self, mocker):
        """client.SQLClient.count"""
        mock = mocker.patch.object(ContextManager, 'execute_query', return_value=SQL_COUNT_RESPONSE)
        output = SQLClient(self.credentials).count('table_name')

        assert output == 12345
        mock.assert_called_once_with('''
            SELECT COUNT(*) FROM table_name;
        '''.strip())

    def test_bounds(self, mocker):
        """client.SQLClient.bounds"""
        mock = mocker.patch.object(ContextManager, 'execute_query', return_value=SQL_BOUNDS_RESPONSE)
        output = SQLClient(self.credentials).bounds('table_name')

        assert output == [
            [-16.2500006525, 28.0999760122],
            [2.65424597028, 43.530016092]
        ]
        mock.assert_called_once_with('''
            SELECT ARRAY[
                ARRAY[st_xmin(geom_env), st_ymin(geom_env)],
                ARRAY[st_xmax(geom_env), st_ymax(geom_env)]
            ] bounds FROM (
                SELECT ST_Extent(the_geom) geom_env
                FROM (SELECT the_geom FROM table_name) q
            ) q;
        '''.strip())

    def test_schema(self, mocker):
        """client.SQLClient.schema"""
        mock = mocker.patch.object(ContextManager, 'execute_query', return_value=SQL_SCHEMA_RESPONSE)
        output = SQLClient(self.credentials).schema('table_name', raw=True)

        assert output == {
            'column_a': 'string',
            'column_b': 'number',
            'column_c': 'geometry'
        }
        mock.assert_called_once_with('''
            SELECT * FROM table_name LIMIT 0;
        '''.strip())

    def test_describe_type_string(self, mocker):
        """client.SQLClient.describe type: string"""
        mock = mocker.patch.object(ContextManager, 'execute_query', return_value=SQL_DESCRIBE_NUMBER)
        client = SQLClient(self.credentials)
        client._get_column_type = lambda t, c: 'string'
        client.describe('table_name', 'column_name')

        mock.assert_called_once_with('''
            SELECT COUNT(*)
            FROM table_name;
        '''.strip())

    def test_describe_type_number(self, mocker):
        """client.SQLClient.describe type: number"""
        mock = mocker.patch.object(ContextManager, 'execute_query', return_value=SQL_DESCRIBE_NUMBER)
        client = SQLClient(self.credentials)
        client._get_column_type = lambda t, c: 'number'
        client.describe('table_name', 'column_name')

        mock.assert_called_once_with('''
            SELECT COUNT(*),AVG(column_name),MIN(column_name),MAX(column_name)
            FROM table_name;
        '''.strip())

    def test_create_table_no_cartodbfy(self, mocker):
        """client.SQLClient.create_table"""
        mocker.patch.object(ContextManager, 'get_schema')
        mock = mocker.patch.object(ContextManager, 'execute_long_running_query')
        columns = OrderedDict()
        columns['id'] = 'INT'
        columns['name'] = 'TEXT'
        SQLClient(self.credentials).create_table('table_name', columns, cartodbfy=False)

        mock.assert_called_once_with('''
            BEGIN;
            ;
            CREATE TABLE table_name (id INT,name TEXT);
            ;
            COMMIT;
        '''.strip())

    def test_create_table_cartodbfy_org_user(self, mocker):
        """client.SQLClient.create_table cartodbfy: organization user"""
        mocker.patch.object(ContextManager, 'get_schema', return_value='user_name')
        mock = mocker.patch.object(ContextManager, 'execute_long_running_query')
        columns = OrderedDict()
        columns['id'] = 'INT'
        columns['name'] = 'TEXT'
        SQLClient(self.credentials).create_table('table_name', columns, if_exists='replace')

        mock.assert_called_once_with('''
            BEGIN;
            DROP TABLE IF EXISTS table_name;
            CREATE TABLE table_name (id INT,name TEXT);
            SELECT CDB_CartoDBFyTable('user_name', 'table_name');
            COMMIT;
        '''.strip())

    def test_create_table_cartodbfy_public_user(self, mocker):
        """client.SQLClient.create_table cartodbfy: public user"""
        mocker.patch.object(ContextManager, 'get_schema', return_value='public')
        mock = mocker.patch.object(ContextManager, 'execute_long_running_query')
        columns = OrderedDict()
        columns['id'] = 'INT'
        columns['name'] = 'TEXT'
        SQLClient(self.credentials).create_table('table_name', columns, if_exists='fail')

        mock.assert_called_once_with('''
            BEGIN;
            ;
            CREATE TABLE table_name (id INT,name TEXT);
            SELECT CDB_CartoDBFyTable('public', 'table_name');
            COMMIT;
        '''.strip())

    def test_insert_table(self, mocker):
        """client.SQLClient.insert_table"""
        mock = mocker.patch.object(ContextManager, 'execute_long_running_query')
        values = OrderedDict()
        values['id'] = [0, 1]
        values['name'] = ['a', 'b']
        SQLClient(self.credentials).insert_table('table_name', values)

        mock.assert_called_once_with('''
            INSERT INTO table_name (id,name) VALUES (0,'a'),(1,'b');
        '''.strip())

    def test_update_table(self, mocker):
        """client.SQLClient.update_table"""
        mock = mocker.patch.object(ContextManager, 'execute_long_running_query')
        SQLClient(self.credentials).update_table('table_name', 'name', 'b', 'id = 0')

        mock.assert_called_once_with('''
            UPDATE table_name SET name='b' WHERE id = 0;
        '''.strip())

    def test_rename_table(self, mocker):
        """client.SQLClient.rename_table"""
        mock = mocker.patch.object(ContextManager, 'execute_long_running_query')
        SQLClient(self.credentials).rename_table('table_name', 'new_table_name')

        mock.assert_called_once_with('''
            ALTER TABLE table_name RENAME TO new_table_name;
        '''.strip())

    def test_drop_table(self, mocker):
        """client.SQLClient.drop_table"""
        mock = mocker.patch.object(ContextManager, 'execute_long_running_query')
        SQLClient(self.credentials).drop_table('table_name')

        mock.assert_called_once_with('''
            DROP TABLE IF EXISTS table_name;
        '''.strip())
