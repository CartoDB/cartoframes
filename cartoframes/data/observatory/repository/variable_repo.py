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
    def _from_client(cls, row):
        # TODO: Map properties
        return row

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
