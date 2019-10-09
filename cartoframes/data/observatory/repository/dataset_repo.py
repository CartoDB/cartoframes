from __future__ import absolute_import

from .entity_repo import EntityRepository


_DATASET_ID_FIELD = 'id'


def get_dataset_repo():
    return _REPO


class DatasetRepository(EntityRepository):

    id_field = _DATASET_ID_FIELD

    def get_all(self, credentials=None):
        self.client.set_user_credentials(credentials)
        return self._get_filtered_entities()

    def get_by_country(self, iso_code3):
        return self._get_filtered_entities('country_id', iso_code3)

    def get_by_category(self, category_id):
        return self._get_filtered_entities('category_id', category_id)

    def get_by_variable(self, variable_id):
        return self._get_filtered_entities('variable_id', variable_id)

    def get_by_geography(self, geography_id):
        return self._get_filtered_entities('geography_id', geography_id)

    def get_by_provider(self, provider_id):
        return self._get_filtered_entities('provider_id', provider_id)

    @classmethod
    def _map_row(cls, row):
        return {
            'id': cls._normalize_field(row, cls.id_field),
            'name': cls._normalize_field(row, 'name'),
            'description': cls._normalize_field(row, 'description'),
            'provider_id': cls._normalize_field(row, 'provider_id'),
            'category_id': cls._normalize_field(row, 'category_id'),
            'data_source_id': cls._normalize_field(row, 'data_source_id'),
            'country_id': cls._normalize_field(row, 'country_id'),
            'lang': cls._normalize_field(row, 'lang'),
            'geography_id': cls._normalize_field(row, 'geography_id'),
            'temporal_aggregation': cls._normalize_field(row, 'temporal_aggregation'),
            'time_coverage': cls._normalize_field(row, 'time_coverage'),
            'update_frequency': cls._normalize_field(row, 'update_frequency'),
            'version': cls._normalize_field(row, 'version'),
            'is_public_data': cls._normalize_field(row, 'is_public_data'),
            'summary_jsonb': cls._normalize_field(row, 'summary_jsonb')
        }

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.dataset import Dataset
        return Dataset

    def _get_rows(self, field=None, value=None):
        return self.client.get_datasets(field, value)


_REPO = DatasetRepository()
