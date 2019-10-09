from __future__ import absolute_import

from .constants import CATEGORY_FILTER, COUNTRY_FILTER, GEOGRAPHY_FILTER, PROVIDER_FILTER, VARIABLE_FILTER
from .entity_repo import EntityRepository


_DATASET_ID_FIELD = 'id'
_DATASET_SLUG_FIELD = 'slug'
_ALLOWED_FILTERS = [CATEGORY_FILTER, COUNTRY_FILTER, GEOGRAPHY_FILTER, PROVIDER_FILTER, VARIABLE_FILTER]


def get_dataset_repo():
    return _REPO


class DatasetRepository(EntityRepository):

    def __init__(self):
        super(DatasetRepository, self).__init__(_DATASET_ID_FIELD, _ALLOWED_FILTERS, _DATASET_SLUG_FIELD)

    def get_by_country(self, iso_code3):
        return self._get_filtered_entities({COUNTRY_FILTER: iso_code3})

    def get_by_category(self, category_id):
        return self._get_filtered_entities({CATEGORY_FILTER: category_id})

    def get_by_variable(self, variable_id):
        return self._get_filtered_entities({VARIABLE_FILTER: variable_id})

    def get_by_geography(self, geography_id):
        return self._get_filtered_entities({GEOGRAPHY_FILTER: geography_id})

    def get_by_provider(self, provider_id):
        return self._get_filtered_entities({PROVIDER_FILTER: provider_id})

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.dataset import Dataset
        return Dataset

    def _get_rows(self, filters=None):
        return self.client.get_datasets(filters)

    def _map_row(self, row):
        return {
            'id': self._normalize_field(row, self.id_field),
            'slug': self._normalize_field(row, 'slug'),
            'name': self._normalize_field(row, 'name'),
            'description': self._normalize_field(row, 'description'),
            'provider_id': self._normalize_field(row, 'provider_id'),
            'category_id': self._normalize_field(row, 'category_id'),
            'data_source_id': self._normalize_field(row, 'data_source_id'),
            'country_id': self._normalize_field(row, 'country_id'),
            'lang': self._normalize_field(row, 'lang'),
            'geography_id': self._normalize_field(row, 'geography_id'),
            'temporal_aggregation': self._normalize_field(row, 'temporal_aggregation'),
            'time_coverage': self._normalize_field(row, 'time_coverage'),
            'update_frequency': self._normalize_field(row, 'update_frequency'),
            'version': self._normalize_field(row, 'version'),
            'is_public_data': self._normalize_field(row, 'is_public_data'),
            'summary_jsonb': self._normalize_field(row, 'summary_jsonb')
        }


_REPO = DatasetRepository()
