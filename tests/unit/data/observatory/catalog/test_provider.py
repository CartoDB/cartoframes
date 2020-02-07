import pandas as pd

from unittest.mock import patch

from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.provider import Provider
from cartoframes.data.observatory.catalog.repository.provider_repo import ProviderRepository
from cartoframes.data.observatory.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.catalog.repository.constants import PROVIDER_FILTER
from .examples import test_datasets, test_provider1, test_providers, db_provider1, test_provider2, db_provider2


class TestProvider(object):

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

    @patch.object(DatasetRepository, 'get_all')
    def test_get_datasets_by_provider(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_provider1.datasets

        # Then
        mocked_repo.assert_called_once_with({PROVIDER_FILTER: test_provider1.id})
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    def test_provider_properties(self):
        # Given
        provider = Provider(db_provider1)

        # When
        provider_id = provider.id
        name = provider.name

        # Then
        assert provider_id == db_provider1['id']
        assert name == db_provider1['name']

    def test_provider_is_exported_as_series(self):
        # Given
        provider = test_provider1

        # When
        provider_series = provider.to_series()

        # Then
        assert isinstance(provider_series, pd.Series)
        assert provider_series['id'] == provider.id

    def test_provider_is_exported_as_dict(self):
        # Given
        provider = Provider(db_provider1)

        # When
        provider_dict = provider.to_dict()

        # Then
        assert isinstance(provider_dict, dict)
        assert provider_dict == db_provider1

    def test_provider_is_represented_with_classname_and_id(self):
        # Given
        provider = Provider(db_provider1)

        # When
        provider_repr = repr(provider)

        # Then
        assert provider_repr == "<Provider.get('{id}')>".format(id=db_provider1['id'])

    def test_provider_is_printed_with_classname(self):
        # Given
        provider = Provider(db_provider1)

        # When
        provider_str = str(provider)

        # Then
        assert provider_str == 'Provider({dict_str})'.format(dict_str=str(db_provider1))

    @patch.object(ProviderRepository, 'get_all')
    def test_get_all_providers(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_providers

        # When
        providers = Provider.get_all()

        # Then
        assert isinstance(providers, list)
        assert isinstance(providers, CatalogList)
        assert providers == test_providers

    def test_provider_list_is_printed_with_classname_and_ids(self):
        # Given
        providers = CatalogList([test_provider1, test_provider2])

        # When
        providers_str = str(providers)

        # Then
        assert providers_str == "[<Provider.get('{id1}')>, <Provider.get('{id2}')>]" \
                                .format(id1=db_provider1['id'], id2=db_provider2['id'])

    def test_provider_list_is_represented_with_classname_and_ids(self):
        # Given
        providers = CatalogList([test_provider1, test_provider2])

        # When
        providers_repr = repr(providers)

        # Then
        assert providers_repr == "[<Provider.get('{id1}')>, <Provider.get('{id2}')>]"\
                                 .format(id1=db_provider1['id'], id2=db_provider2['id'])

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
