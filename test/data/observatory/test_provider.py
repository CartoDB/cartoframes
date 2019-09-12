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

    @patch.object(ProviderRepository, 'by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_provider1

        # When
        provider = Provider.get_by_id('cat1')

        # Then
        assert isinstance(provider, pd.Series)
        assert isinstance(provider, Provider)
        assert provider == test_provider1

    @patch.object(DatasetRepository, 'by_provider')
    def test_get_datasets(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_provider1.datasets()

        # Then
        assert isinstance(datasets, pd.DataFrame)
        assert isinstance(datasets, Datasets)
        assert datasets == test_datasets


class TestProviders(unittest.TestCase):

    @patch.object(ProviderRepository, 'all')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_providers

        # When
        providers = Providers.all()

        # Then
        assert isinstance(providers, pd.DataFrame)
        assert isinstance(providers, Providers)
        assert providers == test_providers

    @patch.object(ProviderRepository, 'by_id')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_provider1

        # When
        provider = Providers.get_by_id('bbva')

        # Then
        assert isinstance(provider, pd.Series)
        assert isinstance(provider, Provider)
        assert provider == test_provider1
