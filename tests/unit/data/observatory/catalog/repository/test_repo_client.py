from unittest.mock import patch

from cartoframes.data.observatory.catalog.repository.repo_client import RepoClient


class TestRepoClient:

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_countries_with_filters(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'key': 'value'}
        repo.get_countries(filters)

        fetch_entity_mock.assert_called_once_with('countries', filters)

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_categories_with_filters(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'key': 'value'}
        repo.get_categories(filters)

        fetch_entity_mock.assert_called_once_with('categories', filters)

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_providers_with_filters(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'key': 'value'}
        repo.get_providers(filters)

        fetch_entity_mock.assert_called_once_with('providers', filters)

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_variables_with_filters(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'key': 'value', 'dataset': 'd_1'}
        repo.get_variables(filters)

        fetch_entity_mock.assert_called_once_with('datasets/d_1/variables', {'key': 'value'})

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_variables_with_id(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'id': 'id_1'}
        repo.get_variables(filters)

        fetch_entity_mock.assert_called_once_with('variables/id_1')

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_variables_groups_with_filters(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'key': 'value', 'dataset': 'd_1'}
        repo.get_variables_groups(filters)

        fetch_entity_mock.assert_called_once_with('datasets/d_1/variables_groups', {'key': 'value'})

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_variables_groups_with_id(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'id': 'id_1'}
        repo.get_variables_groups(filters)

        fetch_entity_mock.assert_called_once_with('variables_groups/id_1')

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_datasets_with_filters(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'key': 'value'}
        repo.get_datasets(filters)

        fetch_entity_mock.assert_called_once_with('datasets', filters)

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_datasets_with_id(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'id': 'id_1'}
        repo.get_datasets(filters)

        fetch_entity_mock.assert_called_once_with('datasets/id_1')

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_datasets_with_id_list(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'id': ['id_1', 'id_2']}
        repo.get_datasets(filters)

        fetch_entity_mock.assert_any_call('datasets/id_1')
        fetch_entity_mock.assert_any_call('datasets/id_2')

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_datasets_with_slug(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'slug': 'slug_1'}
        repo.get_datasets(filters)

        fetch_entity_mock.assert_called_once_with('datasets/slug_1')

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_datasets_slug_list(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'slug': ['slug_1', 'slug_2']}
        repo.get_datasets(filters)

        fetch_entity_mock.assert_any_call('datasets/slug_1')
        fetch_entity_mock.assert_any_call('datasets/slug_2')

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_geographies_with_filters(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'key': 'value'}
        repo.get_geographies(filters)

        fetch_entity_mock.assert_called_once_with('geographies', filters)

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_geographies_with_id(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'id': 'id_1'}
        repo.get_geographies(filters)

        fetch_entity_mock.assert_called_once_with('geographies/id_1')

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_geographies_with_id_list(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'id': ['id_1', 'id_2']}
        repo.get_geographies(filters)

        fetch_entity_mock.assert_any_call('geographies/id_1')
        fetch_entity_mock.assert_any_call('geographies/id_2')

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_geographies_with_slug(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'slug': 'slug_1'}
        repo.get_geographies(filters)

        fetch_entity_mock.assert_called_once_with('geographies/slug_1')

    @patch.object(RepoClient, '_fetch_entity')
    def test_get_geographies_slug_list(self, fetch_entity_mock):
        repo = RepoClient()
        filters = {'slug': ['slug_1', 'slug_2']}
        repo.get_geographies(filters)

        fetch_entity_mock.assert_any_call('geographies/slug_1')
        fetch_entity_mock.assert_any_call('geographies/slug_2')

    @patch.object(RepoClient, '_fetch_entity')
    def test_fetch_entity_id_list(self, fetch_entity_mock):
        fetch_entity_mock.side_effect = lambda _id: None if _id == 'datasets/x' else _id
        repo = RepoClient()
        filters = {'id': ['x', 'a', 'b', 'x', 'c', 'x']}
        datasets = repo.get_datasets(filters)

        fetch_entity_mock.assert_any_call('datasets/a')
        fetch_entity_mock.assert_any_call('datasets/b')
        fetch_entity_mock.assert_any_call('datasets/c')
        fetch_entity_mock.assert_any_call('datasets/x')
        assert datasets == ['datasets/a', 'datasets/b', 'datasets/c']
