import unittest

from cartoframes.data.observatory.geography import Geographies

from cartoframes.data.observatory.repository.geography_repo import GeographyRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_geography1, test_geographies, db_geography1, db_geography2

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestGeographyRepo(unittest.TestCase):

    def setUp(self):
        RepoClient.get_geographies = Mock(return_value=[db_geography1, db_geography2])

    def test_get_all(self):
        # Given
        repo = GeographyRepository()

        # When
        geographies = repo.all()

        # Then
        assert geographies == test_geographies

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_geographies = Mock(return_value=[])
        repo = GeographyRepository()

        # When
        geographies = repo.all()

        # Then
        assert geographies == Geographies([])

    def test_get_by_id(self):
        # Given
        requested_id = test_geography1['id']
        repo = GeographyRepository()

        # When
        geography = repo.by_id(requested_id)

        # Then
        assert geography == test_geography1

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_geographies = Mock(return_value=[])
        requested_id = 'unknown_id'

        # When
        repo = GeographyRepository()
        geography = repo.by_id(requested_id)

        # Then
        assert geography is None
