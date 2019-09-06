import unittest

from cartoframes.data.catalog.geography import Geographies

from cartoframes.data.catalog.repository.geography_repo import GeographyRepository
from cartoframes.data.catalog.repository.repo_client import RepoClient
from data.catalog.examples import test_geography1, test_geographies

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestGeographyRepo(unittest.TestCase):

    def setUp(self):
        mocked_sql_result = [{
            'id': 'carto-do-public-data.tiger.geography_esp_census_2019',
            'name': 'ESP - Census',
            'provider_id': 'bbva',
            'country_iso_code3': 'esp',
            'version': '20190203',
            'is_public_data': True
        }, {
            'id': 'carto-do-public-data.tiger.geography_esp_municipalities_2019',
            'name': 'ESP - Municipalities',
            'provider_id': 'bbva',
            'country_iso_code3': 'esp',
            'version': '20190203',
            'is_public_data': False
        }]

        RepoClient.get_geographies = Mock(return_value=mocked_sql_result)

    def test_get_all(self):
        # Given
        repo = GeographyRepository()

        # When
        geographies = repo.get_all()

        # Then
        assert geographies == test_geographies

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_geographies = Mock(return_value=[])
        repo = GeographyRepository()

        # When
        geographies = repo.get_all()

        # Then
        assert geographies == Geographies([])

    def test_get_by_id(self):
        # Given
        requested_id = test_geography1['id']
        repo = GeographyRepository()

        # When
        geography = repo.get_by_id(requested_id)

        # Then
        assert geography == test_geography1

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_geographies = Mock(return_value=[])
        requested_id = 'unknown_id'

        # When
        repo = GeographyRepository()
        geography = repo.get_by_id(requested_id)

        # Then
        assert geography is None
