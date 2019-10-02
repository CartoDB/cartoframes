import unittest
import pandas as pd

from cartoframes.data.observatory.dataset import Datasets
from cartoframes.data.observatory.provider import Provider, Providers

from cartoframes.data.observatory.repository.provider_repo import ProviderRepository
from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository
from cartoframes.exceptions import DiscoveryException

from .examples import test_datasets, test_provider1, test_providers, db_provider1

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
        provider = Provider.get_by_id('cat1')

        # Then
        assert isinstance(provider, pd.Series)
        assert isinstance(provider, Provider)
        assert provider == test_provider1

    @patch.object(DatasetRepository, 'get_by_provider')
    def test_get_datasets_by_provider(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_provider1.datasets()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets

    def test_get_datasets_by_provider_fails_if_column_Series(self):
        # Given
        provider = test_providers.id

        # Then
        with self.assertRaises(DiscoveryException):
            provider.datasets()


class TestProviders(unittest.TestCase):

    @patch.object(ProviderRepository, 'get_all')
    def test_get_all_providers(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_providers

        # When
        providers = Providers.get_all()

        # Then
        assert isinstance(providers, pd.DataFrame)
        assert isinstance(providers, Providers)
        assert providers == test_providers

    @patch.object(ProviderRepository, 'get_by_id')
    def test_get_provider_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_provider1

        # When
        provider = Providers.get_by_id('bbva')

        # Then
        assert isinstance(provider, pd.Series)
        assert isinstance(provider, Provider)
        assert provider == test_provider1

    @patch.object(ProviderRepository, 'get_all')
    def test_providers_are_indexed_with_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_providers
        provider_id = db_provider1['id']

        # When
        providers = Providers.get_all()
        provider = providers.loc[provider_id]

        # Then
        assert provider == test_provider1

    @patch.object(DatasetRepository, 'get_all')
    def test_providers_slice_is_provider_and_series(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_providers

        # When
        providers = Datasets.get_all()
        provider = providers.iloc[0]

        # Then
        assert isinstance(provider, Provider)
        assert isinstance(provider, pd.Series)
