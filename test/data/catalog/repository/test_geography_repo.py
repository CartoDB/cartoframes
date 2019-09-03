import unittest

from cartoframes.data.catalog.repository.geography_repo import GeographyRepository
from cartoframes.data.catalog.repository.repo_client import RepoClient

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestGeographyRepo(unittest.TestCase):

    test_geograhy1 = {
        'id': 'carto-do-public-data.tiger.geography_esp_census_2019',
        'name': 'ESP - Census',
        'provider_id': 'bbva',
        'country_iso_code3': 'esp',
        'version': '20190203',
        'is_public': True
    }
    test_geography2 = {
        'id': 'carto-do-public-data.tiger.geography_esp_municipalities_2019',
        'name': 'ESP - Municipalities',
        'provider_id': 'bbva',
        'country_iso_code3': 'esp',
        'version': '20190203',
        'is_public': False
    }

    def setUp(self):
        sql_geographies = [{
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

        RepoClient.get_geographies = Mock(return_value=sql_geographies)

    def test_get_all(self):
        # When
        repo = GeographyRepository()
        geographies = repo.get_all()

        # Then
        expected_geographies = [self.test_geograhy1, self.test_geography2]
        self.assertEqual(expected_geographies, geographies)

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_geographies = Mock(return_value=[])

        # When
        repo = GeographyRepository()
        geographies = repo.get_all()

        # Then
        self.assertEqual([], geographies)

    def test_get_by_id(self):
        # Given
        requested_id = self.test_geograhy1['id']

        # When
        repo = GeographyRepository()
        geography = repo.get_by_id(requested_id)

        # Then
        self.assertEqual(self.test_geograhy1, geography)

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_geographies = Mock(return_value=[])
        requested_id = 'unknown_id'

        # When
        repo = GeographyRepository()
        geography = repo.get_by_id(requested_id)

        # Then
        self.assertEqual(None, geography)
