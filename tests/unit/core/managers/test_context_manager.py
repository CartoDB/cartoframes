import pytest

from carto.sql import SQLClient, BatchSQLClient, CopySQLClient

from cartoframes import CartoDataFrame
from cartoframes.auth import Credentials
from cartoframes.core.managers.context_manager import ContextManager
from cartoframes.utils.columns import ColumnInfo


class TestContextManager(object):

    def setup_method(self):
        self.credentials = Credentials('fake_user', 'fake_api')

    def test_execute_query(self, mocker):
        # Given
        mocker.patch('cartoframes.core.managers.context_manager._create_auth_client')
        mock = mocker.patch.object(SQLClient, 'send')

        # When
        cm = ContextManager(self.credentials)
        cm.execute_query('query')

        # Then
        mock.assert_called_once_with('query', True, True, None)

    def test_execute_long_running_query(self, mocker):
        # Given
        mocker.patch('cartoframes.core.managers.context_manager._create_auth_client')
        mock = mocker.patch.object(BatchSQLClient, 'create_and_wait_for_completion')

        # When
        cm = ContextManager(self.credentials)
        cm.execute_long_running_query('query')

        # Then
        mock.assert_called_once_with('query')

    def test_copy_from(self, mocker):
        # Given
        mocker.patch('cartoframes.core.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', return_value=False)
        mock = mocker.patch.object(ContextManager, '_copy_from')
        cdf = CartoDataFrame({'A': [1]})
        columns = [ColumnInfo('A', 'a', 'bigint', False)]

        # When
        cm = ContextManager(self.credentials)
        cm.copy_from(cdf, 'TABLE NAME')

        # Then
        mock.assert_called_once_with(cdf, 'table_name', columns)

    def test_copy_from_exists_fail(self, mocker):
        # Given
        mocker.patch('cartoframes.core.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', return_value=True)
        mocker.patch.object(ContextManager, 'get_schema', return_value='schema')
        cdf = CartoDataFrame({'A': [1]})

        # When
        with pytest.raises(Exception) as e:
            cm = ContextManager(self.credentials)
            cm.copy_from(cdf, 'TABLE NAME', 'fail')

        # Then
        assert str(e.value) == ('Table "schema.table_name" already exists in CARTO. '
                                'Please choose a different `table_name` or use '
                                'if_exists="replace" to overwrite it')

    def test_copy_from_exists_replace(self, mocker):
        # Given
        mocker.patch('cartoframes.core.managers.context_manager._create_auth_client')
        mocker.patch.object(ContextManager, 'has_table', return_value=True)
        mocker.patch.object(ContextManager, 'get_schema', return_value='schema')
        mock = mocker.patch.object(ContextManager, '_create_table_from_columns')
        cdf = CartoDataFrame({'A': [1]})
        columns = [ColumnInfo('A', 'a', 'bigint', False)]

        # When
        cm = ContextManager(self.credentials)
        cm.copy_from(cdf, 'TABLE NAME', 'replace')

        # Then
        mock.assert_called_once_with('table_name', columns, 'schema', True)

    def test_internal_copy_from(self, mocker):
        # Given
        from shapely.geometry import Point
        mocker.patch('cartoframes.core.managers.context_manager._create_auth_client')
        mock = mocker.patch.object(CopySQLClient, 'copyfrom')
        cdf = CartoDataFrame({'A': [1, 2], 'B': [Point(0, 0), Point(1, 1)]})
        columns = [
            ColumnInfo('A', 'a', 'bigint', False),
            ColumnInfo('B', 'b', 'geometry', True)
        ]

        # When
        cm = ContextManager(self.credentials)
        cm._copy_from(cdf, 'table_name', columns)

        # Then
        assert mock.call_args[0][0] == '''
            COPY table_name(a,b) FROM stdin WITH (FORMAT csv, DELIMITER '|', NULL '__null');
        '''.strip()
        assert list(mock.call_args[0][1]) == [
            b'1|0101000020E610000000000000000000000000000000000000\n',
            b'2|0101000020E6100000000000000000F03F000000000000F03F\n'
        ]
