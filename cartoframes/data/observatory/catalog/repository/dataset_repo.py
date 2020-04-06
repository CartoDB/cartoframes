from .constants import CATEGORY_FILTER, COUNTRY_FILTER, GEOGRAPHY_FILTER, PROVIDER_FILTER
from .entity_repo import EntityRepository

DATASET_TYPE = 'dataset'

_DATASET_ID_FIELD = 'id'
_DATASET_SLUG_FIELD = 'slug'
_ALLOWED_FILTERS = [CATEGORY_FILTER, COUNTRY_FILTER, GEOGRAPHY_FILTER, PROVIDER_FILTER]


def get_dataset_repo():
    return _REPO


class DatasetRepository(EntityRepository):

    def __init__(self):
        super(DatasetRepository, self).__init__(_DATASET_ID_FIELD, _ALLOWED_FILTERS, _DATASET_SLUG_FIELD)

    def get_all(self, filters=None, credentials=None):
        if credentials is not None:
            filters = self._add_subscription_ids(filters, credentials, DATASET_TYPE)
            if filters is None:
                return []

        # Using user credentials to fetch entities
        self.client.set_user_credentials(credentials)
        entities = self._get_filtered_entities(filters)
        self.client.reset_user_credentials()
        return entities

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.catalog.dataset import Dataset
        return Dataset

    def _get_rows(self, filters=None):
        return self.client.get_datasets(filters)

    def _map_row(self, row):
        return {
            'slug': self._normalize_field(row, 'slug'),
            'name': self._normalize_field(row, 'name'),
            'description': self._normalize_field(row, 'description'),
            'category_id': self._normalize_field(row, 'category_id'),
            'country_id': self._normalize_field(row, 'country_id'),
            'data_source_id': self._normalize_field(row, 'data_source_id'),
            'provider_id': self._normalize_field(row, 'provider_id'),
            'geography_name': self._normalize_field(row, 'geography_name'),
            'geography_description': self._normalize_field(row, 'geography_description'),
            'temporal_aggregation': self._normalize_field(row, 'temporal_aggregation'),
            'time_coverage': self._normalize_field(row, 'time_coverage'),
            'update_frequency': self._normalize_field(row, 'update_frequency'),
            'is_public_data': self._normalize_field(row, 'is_public_data'),
            'lang': self._normalize_field(row, 'lang'),
            'version': self._normalize_field(row, 'version'),
            'category_name': self._normalize_field(row, 'category_name'),
            'provider_name': self._normalize_field(row, 'provider_name'),
            'summary_json': self._normalize_field(row, 'summary_json'),
            'geography_id': self._normalize_field(row, 'geography_id'),
            'id': self._normalize_field(row, self.id_field)
        }


_REPO = DatasetRepository()
