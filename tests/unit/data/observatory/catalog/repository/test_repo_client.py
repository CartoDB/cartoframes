from unittest import mock
from cartoframes.data.observatory.catalog.repository.constants import CATEGORY_FILTER, COUNTRY_FILTER
from cartoframes.data.observatory.catalog.repository.repo_client import RepoClient
from ..mocks import mocked_do_api_requests_get_datasets
from ..examples import db_dataset1, db_dataset2


class TestRepoClient(object):

    @mock.patch(
        'cartoframes.data.observatory.catalog.repository.repo_client.requests.get',
        side_effect=mocked_do_api_requests_get_datasets
    )
    def test_run_query_with_one_filter(self, mocket_get):
        repo = RepoClient()
        filters = {CATEGORY_FILTER: 'demographics'}
        # Mocked request should return URL filters as a dict:
        result_filters = repo.get_datasets(filters)

        assert result_filters[CATEGORY_FILTER] == 'demographics'

    @mock.patch(
        'cartoframes.data.observatory.catalog.repository.repo_client.requests.get',
        side_effect=mocked_do_api_requests_get_datasets
    )
    def test_run_query_with_multiple_filter(self, mocket_get):
        repo = RepoClient()
        filters = {
            CATEGORY_FILTER: 'demographics',
            COUNTRY_FILTER: 'usa'
        }
        # Mocked request should return URL filters as a dict:
        result_filters = repo.get_datasets(filters)

        assert result_filters[CATEGORY_FILTER] == 'demographics'
        assert result_filters[COUNTRY_FILTER] == 'usa'

    @mock.patch(
        'cartoframes.data.observatory.catalog.repository.repo_client.requests.get',
        side_effect=mocked_do_api_requests_get_datasets
    )
    def test_run_query_with_id_list(self, mocket_get):
        repo = RepoClient()
        filters = {
            'id': ['basicstats_census_1234567a', 'basicstats_municipalities_2345678b']
        }
        # Mocked request should return both datasets in this case:
        datasets = repo.get_datasets(filters)

        assert datasets == [db_dataset1, db_dataset2]
