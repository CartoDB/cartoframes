import pytest

from geopandas import datasets, read_file
from geopandas.tools.crs import CRS

from cartoframes.auth import Credentials
from cartoframes.io.carto import to_carto
from cartoframes.io.managers.context_manager import ContextManager
from cartoframes.viz import Layer

CREDENTIALS = Credentials('fake_user', 'fake_api_key')


def test_wrong_crs_layer():
    # Given
    gdf = read_file(datasets.get_path('nybb'))

    # When
    with pytest.raises(ValueError):
        Layer(gdf)

    # Then
    assert gdf.crs.equals(CRS('epsg:2263'))


def test_transform_crs_layer():
    # Given
    gdf = read_file(datasets.get_path('nybb'))
    gdf.to_crs(epsg=4326, inplace=True)

    # When
    Layer(gdf)  # No error!

    # Then
    assert gdf.crs.equals(CRS('epsg:4326'))


def test_wrong_crs_to_carto():
    # Given
    gdf = read_file(datasets.get_path('nybb'))

    # When
    with pytest.raises(ValueError):
        to_carto(gdf, 'nybb_2263')


def test_transform_crs_to_carto(mocker):
    # Given
    cm_mock = mocker.patch.object(ContextManager, 'copy_from')

    gdf = read_file(datasets.get_path('nybb'))
    gdf.to_crs(epsg=4326, inplace=True)

    # When
    to_carto(gdf, 'nybb_4326', CREDENTIALS)

    # Then
    cm_mock.assert_called_once_with(mocker.ANY, 'nybb_4326', 'fail', True)
