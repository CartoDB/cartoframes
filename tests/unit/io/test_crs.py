import pytest

from geopandas import GeoDataFrame
from shapely.geometry import Point

from cartoframes.auth import Credentials
from cartoframes.io.carto import to_carto
from cartoframes.io.managers.context_manager import ContextManager
from cartoframes.viz import Layer

CREDENTIALS = Credentials('fake_user', 'fake_api_key')


@pytest.mark.parametrize('crs', ['epsg:2263', 'epsg:3395'])
def test_wrong_crs_layer(crs):
    # Given
    gdf = GeoDataFrame({'geometry': [Point([0, 0])]}, crs=crs)

    # When
    Layer(gdf)  # No error!


@pytest.mark.parametrize('crs', ['epsg:2263', 'epsg:3395'])
def test_wrong_crs_to_carto(mocker, crs):
    _ = mocker.patch.object(ContextManager, 'copy_from')

    # Given
    gdf = GeoDataFrame({'geometry': [Point([0, 0])]}, crs=crs)

    # When
    to_carto(gdf, 'table_name', CREDENTIALS, skip_quota_warning=True)  # No error!


def test_transform_crs_layer():
    # Given
    gdf = GeoDataFrame({'geometry': [Point([0, 0])]}, crs='epsg:4326')

    # When
    Layer(gdf)  # No error!


def test_transform_crs_to_carto(mocker):
    cm_mock = mocker.patch.object(ContextManager, 'copy_from')

    # Given
    gdf = GeoDataFrame({'geometry': [Point([0, 0])]}, crs='epsg:4326')

    # When
    to_carto(gdf, 'table_name', CREDENTIALS, skip_quota_warning=True)

    # Then
    cm_mock.assert_called_once_with(mocker.ANY, 'table_name', 'fail', True, 3)
