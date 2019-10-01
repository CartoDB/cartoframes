from .entity_repo import EntityRepository


_DATASET_ID_FIELD = 'id'


def get_dataset_repo():
    return _REPO


class DatasetRepository(EntityRepository):

    id_field = _DATASET_ID_FIELD

    def get_by_country(self, iso_code3):
        return self._get_filtered_entities('country_iso_code3', iso_code3)

    def get_by_category(self, category_id):
        return self._get_filtered_entities('category_id', category_id)

    def get_by_variable(self, variable_id):
        return self._get_filtered_entities('variable_id', variable_id)

    def get_by_geography(self, geography_id):
        return self._get_filtered_entities('geography_id', geography_id)

    def get_by_provider(self, provider_id):
        return self._get_filtered_entities('provider_id', provider_id)

    @classmethod
    def _from_client(cls, row):
        # TODO: Map properties
        return row

    @classmethod
    def _get_single_entity_class(cls):
        from cartoframes.data.observatory.dataset import Dataset
        return Dataset

    @classmethod
    def _get_entity_list_class(cls):
        from cartoframes.data.observatory.dataset import Datasets
        return Datasets

    def _get_rows(self, field=None, value=None):
        return self.client.get_datasets(field, value)


_REPO = DatasetRepository()
