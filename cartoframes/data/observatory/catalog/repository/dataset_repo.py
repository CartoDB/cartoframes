from .constants import CATEGORY_FILTER, COUNTRY_FILTER, GEOGRAPHY_FILTER, PROVIDER_FILTER
from ..subscriptions import get_subscription_ids
from .entity_repo import EntityRepository


_DATASET_ID_FIELD = 'id'
_DATASET_SLUG_FIELD = 'slug'
_ALLOWED_FILTERS = [CATEGORY_FILTER, COUNTRY_FILTER, GEOGRAPHY_FILTER, PROVIDER_FILTER]


def get_dataset_repo():
    return _REPO


class DatasetRepository(EntityRepository):

    def __init__(self):
        super(DatasetRepository, self).__init__(_DATASET_ID_FIELD, _ALLOWED_FILTERS, _DATASET_SLUG_FIELD)

    def get_all(self, filters=None, credentials=None):
        # If credentials are provided, then we only want the user's subscriptions:
        if credentials is not None:
            ids = get_subscription_ids(credentials)
            if len(ids) == 0:
                return []
            elif len(ids) > 0:
                filters = filters if filters else {}
                filters['id'] = ids

        return self._get_filtered_entities(filters)

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.catalog.dataset import Dataset
        return Dataset

    def _get_rows(self, filters=None):
        return self.client.get_datasets(filters)

    def _map_row(self, row):
        return {
            'id': self._normalize_field(row, self.id_field),
            'slug': self._normalize_field(row, 'slug'),
            'name': self._normalize_field(row, 'name'),
            'description': self._normalize_field(row, 'description'),
            'country_id': self._normalize_field(row, 'country_id'),
            'geography_id': self._normalize_field(row, 'geography_id'),
            'geography_name': self._normalize_field(row, 'geography_name'),
            'geography_description': self._normalize_field(row, 'geography_description'),
            'category_id': self._normalize_field(row, 'category_id'),
            'category_name': self._normalize_field(row, 'category_name'),
            'provider_id': self._normalize_field(row, 'provider_id'),
            'provider_name': self._normalize_field(row, 'provider_name'),
            'data_source_id': self._normalize_field(row, 'data_source_id'),
            'lang': self._normalize_field(row, 'lang'),
            'temporal_aggregation': self._normalize_field(row, 'temporal_aggregation'),
            'time_coverage': self._normalize_field(row, 'time_coverage'),
            'update_frequency': self._normalize_field(row, 'update_frequency'),
            'version': self._normalize_field(row, 'version'),
            'is_public_data': self._normalize_field(row, 'is_public_data'),
            'summary_json': self._normalize_field(row, 'summary_json'),
            'available_in': self._normalize_field(row, 'available_in')
        }


_REPO = DatasetRepository()
