from __future__ import absolute_import

from .constants import DATASET_FILTER, VARIABLE_GROUP_FILTER
from .entity_repo import EntityRepository


_VARIABLE_ID_FIELD = 'id'
_VARIABLE_SLUG_FIELD = 'slug'
_ALLOWED_DATASETS = [DATASET_FILTER, VARIABLE_GROUP_FILTER]


def get_variable_repo():
    return _REPO


class VariableRepository(EntityRepository):

    def __init__(self):
        super(VariableRepository, self).__init__(_VARIABLE_ID_FIELD, _ALLOWED_DATASETS, _VARIABLE_SLUG_FIELD)

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.catalog.variable import Variable
        return Variable

    def _get_rows(self, filters=None):
        return self.client.get_variables(filters)

    def _map_row(self, row):
        return {
            'id': self._normalize_field(row, self.id_field),
            'slug': self._normalize_field(row, 'slug'),
            'name': self._normalize_field(row, 'name'),
            'description': self._normalize_field(row, 'description'),
            'column_name': self._normalize_field(row, 'column_name'),
            'db_type': self._normalize_field(row, 'db_type'),
            'dataset_id': self._normalize_field(row, 'dataset_id'),
            'agg_method': self._normalize_field(row, 'agg_method'),
            'variable_group_id': self._normalize_field(row, 'variable_group_id'),
            'starred': self._normalize_field(row, 'starred'),
            'summary_json': self._normalize_field(row, 'summary_json')
        }


_REPO = VariableRepository()
