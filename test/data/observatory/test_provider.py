import unittest
import pandas as pd

from cartoframes.data.observatory.dataset import Datasets
from cartoframes.data.observatory.provider import Provider, Providers

from cartoframes.data.observatory.repository.provider_repo import ProviderRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository

from .examples import test_datasets, test_provider1, test_providers

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestProvider(unittest.TestCase):

    @patch.object(ProviderRepository, 'get_by_id')
    def test_get_provider_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_provider1

        # When
        provider = Provider.get('cat1')

        # Then
        assert isinstance(provider, object)
        assert isinstance(provider, Provider)
        assert provider == test_provider1

    @patch.object(DatasetRepository, 'get_by_provider')
    def test_get_datasets_by_provider(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_provider1.datasets()

        # Then
        assert isinstance(datasets, list)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets

    def test_provider_is_exported_as_series(self):
        # Given
        provider = test_provider1

        # When
        provider_series = provider.to_series()

        # Then
        assert isinstance(provider_series, pd.Series)
        assert provider_series['id'] == provider.id


class TestProviders(unittest.TestCase):

    @patch.object(ProviderRepository, 'get_all')
    def test_get_all_providers(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_providers

        # When
        providers = Providers.get_all()

        # Then
        assert isinstance(providers, list)
        assert isinstance(providers, Providers)
        assert providers == test_providers

    @patch.object(ProviderRepository, 'get_by_id')
    def test_get_provider_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_provider1

        # When
        provider = Providers.get('bbva')

        # Then
        assert isinstance(provider, object)
        assert isinstance(provider, Provider)
        assert provider == test_provider1

    # @patch.object(ProviderRepository, 'get_all')
    # def test_providers_are_indexed_with_id(self, mocked_repo):
    #     # Given
    #     mocked_repo.return_value = test_providers
    #     provider_id = db_provider1['id']
    #
    #     # When
    #     providers = Providers.get_all()
    #     provider = providers.loc[provider_id]
    #
    #     # Then
    #     assert provider == test_provider1

    def test_providers_items_are_obtained_as_provider(self):
        # Given
        providers = test_providers

        # When
        provider = providers[0]

        # Then
        assert isinstance(provider, Provider)
        assert provider == test_provider1

    def test_providers_are_exported_as_dataframe(self):
        # Given
        providers = test_providers
        provider = providers[0]

        # When
        provider_df = providers.to_dataframe()
        sliced_provider = provider_df.iloc[0]

        # Then
        assert isinstance(provider_df, pd.DataFrame)
        assert isinstance(sliced_provider, pd.Series)
        assert sliced_provider.equals(provider.to_series())
