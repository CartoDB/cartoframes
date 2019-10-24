from __future__ import absolute_import


from .constants import CATEGORY_FILTER, COUNTRY_FILTER, GEOGRAPHY_FILTER, PROVIDER_FILTER, VARIABLE_FILTER
from .entity_repo import EntityRepository
from ..entity import CatalogList


_DATASET_ID_FIELD = 'id'
_DATASET_SLUG_FIELD = 'slug'
_ALLOWED_FILTERS = [CATEGORY_FILTER, COUNTRY_FILTER, GEOGRAPHY_FILTER, PROVIDER_FILTER, VARIABLE_FILTER]


def get_dataset_repo():
    return _REPO


class DatasetRepository(EntityRepository):

    def __init__(self):
        super(DatasetRepository, self).__init__(_DATASET_ID_FIELD, _ALLOWED_FILTERS, _DATASET_SLUG_FIELD)

    def get_all(self, filters=None, credentials=None):
        self.client.set_user_credentials(credentials)
        response = self._get_filtered_entities(filters)
        self.client.set_user_credentials(None)
        return response

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.catalog.dataset import CatalogDataset
        return CatalogDataset

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
            'summary_json': self._normalize_field(row, 'summary_json')
        }

    def get_datasets_for_geographies(self, geographies):
        rows = self.client.get_datasets_for_geographies(geographies)
        normalized_data = [self._get_entity_class()(self._map_row(row)) for row in rows]
        return CatalogList(normalized_data)


_REPO = DatasetRepository()
