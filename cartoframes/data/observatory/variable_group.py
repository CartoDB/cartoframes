from .entity import SingleEntity, EntitiesList
from .repository.variable_group_repo import get_variable_group_repo
from .repository.variable_repo import get_variable_repo

_VARIABLE_GROUP_ID_FIELD = 'id'


class VariableGroup(SingleEntity):

    id_field = _VARIABLE_GROUP_ID_FIELD
    entity_repo = get_variable_group_repo()

    @classmethod
    def _get_entities_list_class(cls):
        return VariablesGroups

    def variables(self):
        return get_variable_repo().get_by_variable_group(self._get_id())


class VariablesGroups(EntitiesList):

    id_field = _VARIABLE_GROUP_ID_FIELD
    entity_repo = get_variable_group_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return VariableGroup
