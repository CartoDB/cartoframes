from .entity_repo import EntityRepository


_VARIABLE_ID_FIELD = 'id'


def get_variable_repo():
    return _REPO


class VariableRepository(EntityRepository):

    id_field = _VARIABLE_ID_FIELD

    def get_by_dataset(self, dataset_id):
        return self._get_filtered_entities('dataset_id', dataset_id)

    def get_by_variable_group(self, variable_group_id):
        return self._get_filtered_entities('variable_group_id', variable_group_id)

    @classmethod
    def _map_row(cls, row):
        return {
            'id': row[cls.id_field],
            'name': row['name'],
            'description': row['description'],
            'column_name': row['column_name'],
            'db_type': row['db_type'],
            'dataset_id': row['dataset_id'],
            'agg_method': row['agg_method'],
            'variable_group_id': row['variable_group_id'],
            'starred': row['starred'],
            'summary_jsonb': row['summary_jsonb']
        }

    @classmethod
    def _get_single_entity_class(cls):
        from cartoframes.data.observatory.variable import Variable
        return Variable

    @classmethod
    def _get_entity_list_class(cls):
        from cartoframes.data.observatory.variable import Variables
        return Variables

    def _get_rows(self, field=None, value=None):
        return self.client.get_variables(field, value)


_REPO = VariableRepository()
