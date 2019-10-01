from cartoframes.exceptions import DiscoveryException
from .repo_client import RepoClient


def get_dataset_repo():
    return _REPO


class DatasetRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return self._to_datasets(self.client.get_datasets())

    def get_by_id(self, dataset_id):
        result = self.client.get_datasets('id', dataset_id)

        if len(result) == 0:
            raise DiscoveryException('The id does not correspond with any existing dataset in the catalog. '
                                     'You can check the full list of available datasets with Datasets.get_all()')

        return self._to_dataset(result[0])

    def get_by_country(self, iso_code3):
        return self._to_datasets(self.client.get_datasets('country_iso_code3', iso_code3))

    def get_by_category(self, category_id):
        return self._to_datasets(self.client.get_datasets('category_id', category_id))

    def get_by_variable(self, variable_id):
        return self._to_datasets(self.client.get_datasets('variable_id', variable_id))

    def get_by_geography(self, geography_id):
        return self._to_datasets(self.client.get_datasets('geography_id', geography_id))

    def get_by_provider(self, provider_id):
        return self._to_datasets(self.client.get_datasets('provider_id', provider_id))

    @staticmethod
    def _to_dataset(result):
        from cartoframes.data.observatory.dataset import Dataset

        return Dataset(result)

    @staticmethod
    def _to_datasets(results):
        if len(results) == 0:
            return None

        from cartoframes.data.observatory.dataset import Datasets

        return Datasets(DatasetRepository._to_dataset(result) for result in results)


_REPO = DatasetRepository()
