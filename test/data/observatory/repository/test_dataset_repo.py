import unittest

from cartoframes.data.observatory.dataset import Datasets

from cartoframes.data.observatory.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_dataset1, test_datasets, db_dataset1, db_dataset2

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestDatasetRepo(unittest.TestCase):

    def setUp(self):
        RepoClient.get_datasets = Mock(return_value=[db_dataset1, db_dataset2])

    def test_get_all(self):
        # Given
        repo = DatasetRepository()

        # When
        datasets = repo.get_all()

        # Then
        assert datasets == test_datasets

    def test_get_all_when_empty(self):
        # Given
        RepoClient.get_datasets = Mock(return_value=[])
        repo = DatasetRepository()

        # When
        datasets = repo.get_all()

        # Then
        assert datasets == Datasets([])

    def test_get_by_id(self,):
        # Given
        requested_id = test_dataset1['id']
        repo = DatasetRepository()

        # When
        dataset = repo.get_by_id(requested_id)

        # Then
        assert dataset == test_dataset1

    def test_get_by_id_unknown(self):
        # Given
        RepoClient.get_datasets = Mock(return_value=[])
        requested_id = 'unknown_id'
        repo = DatasetRepository()

        # When
        dataset = repo.get_by_id(requested_id)

        # Then
        assert dataset is None
