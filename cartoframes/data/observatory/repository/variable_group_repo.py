from .entity_repo import EntityRepository


_VARIABLE_GROUP_ID_FIELD = 'id'


def get_variable_group_repo():
    return _REPO


class VariableGroupRepository(EntityRepository):

    id_field = _VARIABLE_GROUP_ID_FIELD

    def get_by_dataset(self, dataset_id):
        return self._get_filtered_entities('dataset_id', dataset_id)

    @classmethod
    def _from_client(cls, row):
        # TODO: Map properties
        return row

    @classmethod
    def _get_single_entity_class(cls):
        from cartoframes.data.observatory.variable_group import VariableGroup
        return VariableGroup

    @classmethod
    def _get_entity_list_class(cls):
        from cartoframes.data.observatory.variable_group import VariablesGroups
        return VariablesGroups

    def _get_rows(self, field=None, value=None):
        return self.client.get_variables_groups(field, value)


_REPO = VariableGroupRepository()
