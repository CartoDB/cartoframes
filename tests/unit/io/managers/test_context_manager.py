from collections import namedtuple

import pytest

from carto.datasets import DatasetManager
from carto.sql import SQLClient, BatchSQLClient, CopySQLClient
from carto.exceptions import CartoRateLimitException

from pandas import DataFrame
from geopandas import GeoDataFrame
from cartoframes.auth import Credentials
from cartoframes.io.managers.context_manager import ContextManager, DEFAULT_RETRY_TIMES, retry_copy
from cartoframes.utils.columns import ColumnInfo


class TestContextManager(object):

    def setup_method(self):
        self.credentials = Credentials('fake_user', 'fake_api')

    def test_execute_query(self, mocker):
        # Given
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mock = mocker.patch.object(SQLClient, 'send')

        # When
        cm = ContextManager(self.credentials)
        cm.execute_query('query')

        # Then
        mock.assert_called_once_with('query', True, True, None)

    def test_execute_long_running_query(self, mocker):
        # Given
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mock = mocker.patch.object(BatchSQLClient, 'create_and_wait_for_completion')

        # When
        cm = ContextManager(self.credentials)
        cm.execute_long_running_query('query')

        # Then
        mock.assert_called_once_with('query')

    def test_copy_to(self, mocker):
        # Given
        query = '__query__'
        columns = [ColumnInfo('A', 'a', 'bigint', False)]
        mocker.patch.object(ContextManager, 'compute_query', return_value=query)
        mocker.patch.object(ContextManager, '_get_query_columns_info', return_value=columns)
        mock = mocker.patch.object(ContextManager, '_copy_to')

        # When
        cm = ContextManager(self.credentials)
        cm.copy_to(query)

        # Then
        mock.assert_called_once_with('SELECT "A" FROM (__query__) _q', columns, 3)

    def test_copy_from(self, mocker):
        # Given
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', return_value=False)
        mocker.patch.object(ContextManager, 'get_schema', return_value='schema')
        mock_create_table = mocker.patch.object(ContextManager, 'execute_query')
        mock = mocker.patch.object(ContextManager, '_copy_from')
        df = DataFrame({'A': [1]})
        columns = [ColumnInfo('A', 'a', 'bigint', False)]

        # When
        cm = ContextManager(self.credentials)
        cm.copy_from(df, 'TABLE NAME')

        # Then
        mock_create_table.assert_called_once_with('''
            BEGIN; CREATE TABLE table_name ("a" bigint); COMMIT;
        '''.strip())
        mock.assert_called_once_with(df, 'table_name', columns, DEFAULT_RETRY_TIMES)

    def test_copy_from_exists_fail(self, mocker):
        # Given
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', return_value=True)
        mocker.patch.object(ContextManager, 'get_schema', return_value='schema')
        df = DataFrame({'A': [1]})

        # When
        with pytest.raises(Exception) as e:
            cm = ContextManager(self.credentials)
            cm.copy_from(df, 'TABLE NAME', 'fail')

        # Then
        assert str(e.value) == ('Table "schema.table_name" already exists in your CARTO account. '
                                'Please choose a different `table_name` or use '
                                'if_exists="replace" to overwrite it.')

    def test_copy_from_exists_replace_truncate_and_drop_add_columns(self, mocker):
        # Given
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', return_value=True)
        mocker.patch.object(ContextManager, 'get_schema', return_value='schema')
        mock = mocker.patch.object(ContextManager, '_truncate_and_drop_add_columns')
        df = DataFrame({'A': [1]})
        columns = [ColumnInfo('A', 'a', 'bigint', False)]

        # When
        cm = ContextManager(self.credentials)
        cm.copy_from(df, 'TABLE NAME', 'replace')

        # Then
        mock.assert_called_once_with('table_name', 'schema', columns, [])

    def test_copy_from_exists_replace_truncate(self, mocker):
        # Given
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', return_value=True)
        mocker.patch.object(ContextManager, 'get_schema', return_value='schema')
        mocker.patch.object(ContextManager, '_compare_columns', return_value=True)
        mock = mocker.patch.object(ContextManager, '_truncate_table')
        df = DataFrame({'A': [1]})

        # When
        cm = ContextManager(self.credentials)
        cm.copy_from(df, 'TABLE NAME', 'replace')

        # Then
        mock.assert_called_once_with('table_name', 'schema')

    def test_internal_copy_from(self, mocker):
        # Given
        from shapely.geometry import Point
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mock = mocker.patch.object(CopySQLClient, 'copyfrom')
        gdf = GeoDataFrame({'A': [1, 2], 'B': [Point(0, 0), Point(1, 1)]})
        columns = [
            ColumnInfo('A', 'a', 'bigint', False),
            ColumnInfo('B', 'b', 'geometry', True)
        ]

        # When
        cm = ContextManager(self.credentials)
        cm._copy_from(gdf, 'table_name', columns)

        # Then
        assert mock.call_args[0][0] == '''
            COPY table_name("a","b") FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
        '''.strip()
        assert list(mock.call_args[0][1]) == [
            b'1|0101000020E610000000000000000000000000000000000000\n',
            b'2|0101000020E6100000000000000000F03F000000000000F03F\n'
        ]

    def test_rename_table(self, mocker):
        # Given
        def has_table(table_name):
            if table_name == 'table_name':
                return True
            elif table_name == 'new_table_name':
                return False
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', side_effect=has_table)
        mock = mocker.patch.object(ContextManager, '_rename_table')

        # When
        cm = ContextManager(self.credentials)
        result = cm.rename_table('table_name', 'NEW TABLE NAME')

        # Then
        mock.assert_called_once_with('table_name', 'new_table_name')
        assert result == 'new_table_name'

    def test_rename_table_equal(self, mocker):
        # When
        with pytest.raises(Exception) as e:
            cm = ContextManager(self.credentials)
            cm.rename_table('table_name', 'TABLE NAME')

        # Then
        assert str(e.value) == ('Table names are equal. Please choose a different table name.')

    def test_rename_table_orig_not_exist(self, mocker):
        # Given
        def has_table(table_name):
            if table_name == 'table_name':
                return False
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', side_effect=has_table)

        # When
        with pytest.raises(Exception) as e:
            cm = ContextManager(self.credentials)
            cm.rename_table('table_name', 'NEW TABLE NAME')

        # Then
        assert str(e.value) == ('Table "table_name" does not exist in your CARTO account.')

    def test_rename_table_dest_exists_fail(self, mocker):
        # Given
        def has_table(table_name):
            if table_name == 'table_name':
                return True
            elif table_name == 'new_table_name':
                return True
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', side_effect=has_table)

        # When
        with pytest.raises(Exception) as e:
            cm = ContextManager(self.credentials)
            cm.rename_table('table_name', 'NEW TABLE NAME', 'fail')

        # Then
        assert str(e.value) == ('Table "new_table_name" already exists in your CARTO account. '
                                'Please choose a different `new_table_name` or use '
                                'if_exists="replace" to overwrite it.')

    def test_rename_table_dest_exists_replace(self, mocker):
        # Given
        def has_table(table_name):
            if table_name == 'table_name':
                return True
            elif table_name == 'new_table_name':
                return True
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', side_effect=has_table)
        mock = mocker.patch.object(ContextManager, '_rename_table')

        # When
        cm = ContextManager(self.credentials)
        result = cm.rename_table('table_name', 'NEW TABLE NAME', 'replace')

        # Then
        mock.assert_called_once_with('table_name', 'new_table_name')
        assert result == 'new_table_name'

    def test_list_tables(self, mocker):
        # Given
        Dataset = namedtuple('Dataset', ['name', 'updated_at'])

        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(DatasetManager, 'filter', return_value=[
            Dataset('table_zero', 1), Dataset('table_one', 0)
        ])

        # When
        cm = ContextManager(self.credentials)
        tables = cm.list_tables()

        # Then
        assert DataFrame(['table_zero', 'table_one'], columns=['tables']).equals(tables)

    def test_list_tables_empty(self, mocker):
        # Given
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(DatasetManager, 'filter', return_value=[])

        # When
        cm = ContextManager(self.credentials)
        tables = cm.list_tables()

        # Then
        assert DataFrame(columns=['tables']).equals(tables)

    def test_retry_copy_decorator(self):
        @retry_copy
        def test_function(retry_times):
            class ResponseMock:
                def __init__(self):
                    self.text = 'My text'
                    self.headers = {
                        'Carto-Rate-Limit-Limit': 1,
                        'Carto-Rate-Limit-Remaining': 1,
                        'Retry-After': 1,
                        'Carto-Rate-Limit-Reset': 1
                    }
            response_mock = ResponseMock()
            raise CartoRateLimitException(response_mock)

        with pytest.raises(CartoRateLimitException):
            test_function(retry_times=0)

    def test_create_table_from_query_cartodbfy(self, mocker):
        # Given
        mocker.patch.object(ContextManager, 'has_table', return_value=False)
        mocker.patch.object(ContextManager, 'get_schema', return_value='schema')
        mock = mocker.patch.object(ContextManager, 'execute_long_running_query')

        # When
        cm = ContextManager(self.credentials)
        cm.create_table_from_query('SELECT * FROM table_name', '__new_table_name__', if_exists='fail', cartodbfy=True)

        # Then
        mock.assert_called_with("SELECT CDB_CartodbfyTable('schema', '__new_table_name__')")

    def test_create_table_from_query_cartodbfy_default(self, mocker):
        # Given
        mocker.patch.object(ContextManager, 'has_table', return_value=False)
        mocker.patch.object(ContextManager, 'get_schema', return_value='schema')
        mock = mocker.patch.object(ContextManager, 'execute_long_running_query')

        # When
        cm = ContextManager(self.credentials)
        cm.create_table_from_query('SELECT * FROM table_name', '__new_table_name__', if_exists='fail')

        # Then
        mock.assert_called_with("SELECT CDB_CartodbfyTable('schema', '__new_table_name__')")
