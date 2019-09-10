from cartoframes.data.catalog.repository.repo_client import RepoClient


def get_dataset_repo():
    return DatasetRepository()


class DatasetRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return self._to_datasets(self.client.get_datasets())

    def get_by_id(self, dataset_id):
        result = self.client.get_datasets('id', dataset_id)

        if len(result) == 0:
            return None

        return self._to_dataset(result[0])

    def get_by_country(self, iso3):
        return self._to_datasets(self.client.get_datasets('country_iso_code3', iso3))

    def get_by_category(self, category_id):
        return self._to_datasets(self.client.get_datasets('category_id', category_id))

    def get_by_variable(self, variable_id):
        return self._to_datasets(self.client.get_datasets('variable_id', variable_id))

    def get_by_geography(self, geography_id):
        return self._to_datasets(self.client.get_datasets('geography_id', geography_id))

    @staticmethod
    def _to_dataset(result):
        from cartoframes.data.catalog.dataset import Dataset

        return Dataset({
            'id': result['id'],
            'name': result['name'],
            'provider_id': result['provider_id'],
            'category_id': result['category_id'],
            'country_iso_code3': result['country_iso_code3'],
            'geography_id': result['geography_id'],
            'temporal_aggregations': result['temporalaggregations'],
            'time_coverage': result['time_coverage'],
            'group_id': result['datasets_groups_id'],
            'version': result['version'],
            'is_public': result['is_public_data']
        })

    @staticmethod
    def _to_datasets(results):
        from cartoframes.data.catalog.dataset import Datasets

        return Datasets(DatasetRepository._to_dataset(result) for result in results)
