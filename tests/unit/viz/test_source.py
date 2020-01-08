import pytest
import numpy as np
import pandas as pd
import geopandas as gpd

from cartoframes.auth import Credentials
from cartoframes.viz.source import Source
from cartoframes.io.managers.context_manager import ContextManager


def setup_mocks(mocker):
    mocker.patch.object(ContextManager, 'compute_query')


class TestSource(object):
    def test_is_source_defined(self):
        """Source"""
        assert Source is not None

    def test_source_get_credentials_username(self, mocker):
        """Source should return the correct credentials when username is provided"""
        setup_mocks(mocker)
        source = Source('faketable', credentials=Credentials(
            username='fakeuser', api_key='1234'))

        credentials = source.get_credentials()

        assert credentials['username'] == 'fakeuser'
        assert credentials['api_key'] == '1234'
        assert credentials['base_url'] == 'https://fakeuser.carto.com'

    def test_source_get_credentials_base_url(self, mocker):
        """Source should return the correct credentials when base_url is provided"""
        setup_mocks(mocker)
        source = Source('faketable', credentials=Credentials(
            base_url='https://fakeuser.carto.com'))

        credentials = source.get_credentials()

        assert credentials['username'] == 'user'
        assert credentials['api_key'] == 'default_public'
        assert credentials['base_url'] == 'https://fakeuser.carto.com'

    def test_source_no_credentials(self):
        """Source should raise an exception if there are no credentials"""
        with pytest.raises(ValueError) as e:
            Source('faketable')

        assert str(e.value) == ('Credentials attribute is required. '
                                'Please pass a `Credentials` instance or use '
                                'the `set_default_credentials` function.')

    def test_dates_in_source(self):
        df = pd.DataFrame({
            'date_column': ['2019-11-10', '2019-11-11'],
            'lat': [1, 2],
            'lon': [1, 2]
        })
        df['date_column'] = pd.to_datetime(df['date_column'])
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))

        assert df.dtypes['date_column'] == np.dtype('datetime64[ns]')

        source = Source(gdf)

        assert source.datetime_column_names == ['date_column']
        assert source.gdf.dtypes['date_column'] == np.object
