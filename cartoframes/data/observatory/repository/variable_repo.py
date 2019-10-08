from __future__ import absolute_import

from .entity_repo import EntityRepository


_VARIABLE_ID_FIELD = 'id'


def get_variable_repo():
    return _REPO


class VariableRepository(EntityRepository):

    id_field = _VARIABLE_ID_FIELD

    def get_by_dataset(self, dataset_id):
        return self._get_filtered_entities({'dataset_id': dataset_id})

    def get_by_variable_group(self, variable_group_id):
        return self._get_filtered_entities({'variable_group_id': variable_group_id})

    @classmethod
    def _map_row(cls, row):
        return {
            'id': cls._normalize_field(row, cls.id_field),
            'name': cls._normalize_field(row, 'name'),
            'description': cls._normalize_field(row, 'description'),
            'column_name': cls._normalize_field(row, 'column_name'),
            'db_type': cls._normalize_field(row, 'db_type'),
            'dataset_id': cls._normalize_field(row, 'dataset_id'),
            'agg_method': cls._normalize_field(row, 'agg_method'),
            'variable_group_id': cls._normalize_field(row, 'variable_group_id'),
            'starred': cls._normalize_field(row, 'starred'),
            'summary_jsonb': cls._normalize_field(row, 'summary_jsonb')
        }

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.variable import Variable
        return Variable

    def _get_rows(self, filters=None):
        return self.client.get_variables(filters)


_REPO = VariableRepository()
