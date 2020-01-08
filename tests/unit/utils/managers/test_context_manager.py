import pytest

from carto.sql import SQLClient, BatchSQLClient, CopySQLClient

from pandas import DataFrame
from geopandas import GeoDataFrame
from cartoframes.auth import Credentials
from cartoframes.io.managers.context_manager import ContextManager
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

    def test_copy_from(self, mocker):
        # Given
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', return_value=False)
        mock = mocker.patch.object(ContextManager, '_copy_from')
        df = DataFrame({'A': [1]})
        columns = [ColumnInfo('A', 'a', 'bigint', False)]

        # When
        cm = ContextManager(self.credentials)
        cm.copy_from(df, 'TABLE NAME')

        # Then
        mock.assert_called_once_with(df, 'table_name', columns)

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

    def test_copy_from_exists_replace(self, mocker):
        # Given
        mocker.patch('cartoframes.io.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', return_value=True)
        mocker.patch.object(ContextManager, 'get_schema', return_value='schema')
        mock = mocker.patch.object(ContextManager, '_create_table_from_columns')
        df = DataFrame({'A': [1]})
        columns = [ColumnInfo('A', 'a', 'bigint', False)]

        # When
        cm = ContextManager(self.credentials)
        cm.copy_from(df, 'TABLE NAME', 'replace')

        # Then
        mock.assert_called_once_with('table_name', columns, 'schema', True)

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
            COPY table_name(a,b) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
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
