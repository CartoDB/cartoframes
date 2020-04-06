import pytest

from pandas import Index
from geopandas import GeoDataFrame
from shapely.geometry import Point

from cartoframes.auth import Credentials
from cartoframes.io.managers.context_manager import ContextManager
from cartoframes.io.carto import read_carto, to_carto, copy_table, create_table_from_query


CREDENTIALS = Credentials('fake_user', 'fake_api_key')


def test_read_carto(mocker):
    # Given
    cm_mock = mocker.patch.object(ContextManager, 'copy_to')
    cm_mock.return_value = GeoDataFrame({
        'cartodb_id': [1, 2, 3],
        'the_geom': [
            '010100000000000000000000000000000000000000',
            '010100000000000000000024400000000000002e40',
            '010100000000000000000034400000000000003e40'
        ]
    })
    expected = GeoDataFrame({
        'cartodb_id': [1, 2, 3],
        'the_geom': [
            Point([0, 0]),
            Point([10, 15]),
            Point([20, 30])
        ]
    }, geometry='the_geom')

    # When
    gdf = read_carto('__source__', CREDENTIALS)

    # Then
    cm_mock.assert_called_once_with('__source__', None, None, 3)
    assert expected.equals(gdf)
    assert gdf.crs == 'epsg:4326'


def test_read_carto_wrong_source(mocker):
    # When
    with pytest.raises(ValueError) as e:
        read_carto(1234)

    # Then
    assert str(e.value) == 'Wrong source. You should provide a valid table_name or SQL query.'


def test_read_carto_wrong_credentials(mocker):
    # When
    with pytest.raises(ValueError) as e:
        read_carto('__source__', 1234)

    # Then
    assert str(e.value) == 'Credentials attribute is required. Please pass a `Credentials` ' + \
                           'instance or use the `set_default_credentials` function.'


def test_read_carto_limit(mocker):
    # Given
    mocker.patch('cartoframes.utils.geom_utils.set_geometry')
    cm_mock = mocker.patch.object(ContextManager, 'copy_to')

    # When
    read_carto('__source__', CREDENTIALS, limit=1)

    # Then
    cm_mock.assert_called_once_with('__source__', None, 1, 3)


def test_read_carto_retry_times(mocker):
    # Given
    mocker.patch('cartoframes.utils.geom_utils.set_geometry')
    cm_mock = mocker.patch.object(ContextManager, 'copy_to')

    # When
    read_carto('__source__', CREDENTIALS, retry_times=1)

    # Then
    cm_mock.assert_called_once_with('__source__', None, None, 1)


def test_read_carto_schema(mocker):
    # Given
    mocker.patch('cartoframes.utils.geom_utils.set_geometry')
    cm_mock = mocker.patch.object(ContextManager, 'copy_to')

    # When
    read_carto('__source__', CREDENTIALS, schema='__schema__')

    # Then
    cm_mock.assert_called_once_with('__source__', '__schema__', None, 3)


def test_read_carto_index_col_exists(mocker):
    # Given
    cm_mock = mocker.patch.object(ContextManager, 'copy_to')
    cm_mock.return_value = GeoDataFrame({
        'cartodb_id': [1, 2, 3],
        'the_geom': [
            '010100000000000000000000000000000000000000',
            '010100000000000000000024400000000000002e40',
            '010100000000000000000034400000000000003e40'
        ]
    })
    expected = GeoDataFrame({
        'the_geom': [
            Point([0, 0]),
            Point([10, 15]),
            Point([20, 30])
        ]
    }, geometry='the_geom', index=Index([1, 2, 3], name='cartodb_id'))

    # When
    gdf = read_carto('__source__', CREDENTIALS, index_col='cartodb_id')

    # Then
    assert expected.equals(gdf)


def test_read_carto_index_col_not_exists(mocker):
    # Given
    cm_mock = mocker.patch.object(ContextManager, 'copy_to')
    cm_mock.return_value = GeoDataFrame({
        'cartodb_id': [1, 2, 3],
        'the_geom': [
            '010100000000000000000000000000000000000000',
            '010100000000000000000024400000000000002e40',
            '010100000000000000000034400000000000003e40'
        ]
    })
    expected = GeoDataFrame({
        'cartodb_id': [1, 2, 3],
        'the_geom': [
            Point([0, 0]),
            Point([10, 15]),
            Point([20, 30])
        ]
    }, geometry='the_geom', index=Index([0, 1, 2], name='rename_index'))

    # When
    gdf = read_carto('__source__', CREDENTIALS, index_col='rename_index')

    # Then
    assert expected.equals(gdf)


def test_read_carto_decode_geom_false(mocker):
    # Given
    cm_mock = mocker.patch.object(ContextManager, 'copy_to')
    cm_mock.return_value = GeoDataFrame({
        'cartodb_id': [1, 2, 3],
        'the_geom': [
            '010100000000000000000000000000000000000000',
            '010100000000000000000024400000000000002e40',
            '010100000000000000000034400000000000003e40'
        ]
    })
    expected = GeoDataFrame({
        'cartodb_id': [1, 2, 3],
        'the_geom': [
            '010100000000000000000000000000000000000000',
            '010100000000000000000024400000000000002e40',
            '010100000000000000000034400000000000003e40'
        ]
    })

    # When
    gdf = read_carto('__source__', CREDENTIALS, decode_geom=False)

    # Then
    assert expected.equals(gdf)


def test_to_carto(mocker):
    # Given
    table_name = '__table_name__'
    cm_mock = mocker.patch.object(ContextManager, 'copy_from')
    cm_mock.return_value = table_name
    df = GeoDataFrame({'geometry': [Point([0, 0])]})

    # When
    norm_table_name = to_carto(df, table_name, CREDENTIALS)

    # Then
    assert cm_mock.call_args[0][1] == table_name
    assert cm_mock.call_args[0][2] == 'fail'
    assert cm_mock.call_args[0][3] is True
    assert norm_table_name == table_name


def test_to_carto_wrong_dataframe(mocker):
    # When
    with pytest.raises(ValueError) as e:
        to_carto(1234, '')

    # Then
    assert str(e.value) == 'Wrong dataframe. You should provide a valid DataFrame instance.'


def test_to_carto_wrong_table_name(mocker):
    # Given
    df = GeoDataFrame({'geometry': [Point([0, 0])]})

    # When
    with pytest.raises(ValueError) as e:
        to_carto(df, 1234)

    # Then
    assert str(e.value) == 'Wrong table name. You should provide a valid table name.'


def test_to_carto_wrong_credentials(mocker):
    # Given
    df = GeoDataFrame({'geometry': [Point([0, 0])]})

    # When
    with pytest.raises(ValueError) as e:
        to_carto(df, '__table_name__', 1234)

    # Then
    assert str(e.value) == 'Credentials attribute is required. Please pass a `Credentials` ' + \
                           'instance or use the `set_default_credentials` function.'


def test_to_carto_wrong_if_exists(mocker):
    # Given
    df = GeoDataFrame({'geometry': [Point([0, 0])]})

    # When
    with pytest.raises(ValueError) as e:
        to_carto(df, '__table_name__', if_exists='keep_calm')

    # Then
    assert str(e.value) == 'Wrong option for the `if_exists` param. You should provide: fail, replace, append.'


def test_to_carto_if_exists_replace(mocker):
    # Given
    cm_mock = mocker.patch.object(ContextManager, 'copy_from')
    df = GeoDataFrame({'geometry': [Point([0, 0])]})

    # When
    to_carto(df, '__table_name__', CREDENTIALS, if_exists='replace')

    # Then
    assert cm_mock.call_args[0][2] == 'replace'


def test_to_carto_no_cartodbfy(mocker):
    # Given
    cm_mock = mocker.patch.object(ContextManager, 'copy_from')
    df = GeoDataFrame({'geometry': [Point([0, 0])]})

    # When
    to_carto(df, '__table_name__', CREDENTIALS, cartodbfy=False)

    # Then
    assert cm_mock.call_args[0][3] is False


def test_to_carto_replace_geometry(mocker):
    # Given
    cm_mock = mocker.patch.object(ContextManager, 'copy_from')
    df = GeoDataFrame({'geom': 'POINT(1 1)', 'geometry': [Point([0, 0])]})

    # When
    to_carto(df, '__table_name__', CREDENTIALS, geom_col='geom', cartodbfy=False)

    # Then
    assert str(cm_mock.call_args[0][0]).strip() == 'the_geom\n0  POINT (1.00000 1.00000)'


def test_copy_table_wrong_table_name(mocker):
    # When
    with pytest.raises(ValueError) as e:
        copy_table(1234, '__new_table_name__')

    # Then
    assert str(e.value) == 'Wrong table name. You should provide a valid table name.'


def test_copy_table_wrong_new_table_name(mocker):
    # When
    with pytest.raises(ValueError) as e:
        copy_table('__table_name__', 1234)

    # Then
    assert str(e.value) == 'Wrong new table name. You should provide a valid table name.'


def test_copy_table_wrong_credentials(mocker):
    # When
    with pytest.raises(ValueError) as e:
        copy_table('__table_name__', '__new_table_name__', 1234)

    # Then
    assert str(e.value) == 'Credentials attribute is required. Please pass a `Credentials` ' + \
                           'instance or use the `set_default_credentials` function.'


def test_copy_table_wrong_if_exists(mocker):
    # When
    with pytest.raises(ValueError) as e:
        copy_table('__table_name__', '__new_table_name__', if_exists='keep_calm')

    # Then
    assert str(e.value) == 'Wrong option for the `if_exists` param. You should provide: fail, replace, append.'


def test_create_table_from_query_wrong_query(mocker):
    # When
    with pytest.raises(ValueError) as e:
        create_table_from_query('WRONG SQL QUERY', '__new_table_name__')

    # Then
    assert str(e.value) == 'Wrong query. You should provide a valid SQL query.'


def test_create_table_from_query_wrong_new_table_name(mocker):
    # When
    with pytest.raises(ValueError) as e:
        create_table_from_query('SELECT * FROM table', 1234)

    # Then
    assert str(e.value) == 'Wrong new table name. You should provide a valid table name.'


def test_create_table_from_query_wrong_credentials(mocker):
    # When
    with pytest.raises(ValueError) as e:
        create_table_from_query('SELECT * FROM table', '__new_table_name__', 1234)

    # Then
    assert str(e.value) == 'Credentials attribute is required. Please pass a `Credentials` ' + \
                           'instance or use the `set_default_credentials` function.'


def test_create_table_from_query_wrong_if_exists(mocker):
    # When
    with pytest.raises(ValueError) as e:
        create_table_from_query('SELECT * FROM table', '__new_table_name__', if_exists='keep_calm')

    # Then
    assert str(e.value) == 'Wrong option for the `if_exists` param. You should provide: fail, replace, append.'
