from .entity import SingleEntity, EntitiesList
from .repository.variable_group_repo import get_variable_group_repo
from .repository.variable_repo import get_variable_repo

_VARIABLE_GROUP_ID_FIELD = 'id'


class VariableGroup(SingleEntity):

    id_field = _VARIABLE_GROUP_ID_FIELD
    entity_repo = get_variable_group_repo()

    def variables(self):
        return get_variable_repo().get_by_variable_group(self.id)

    @property
    def id(self):
        return self.data[self.id_field]

    @property
    def name(self):
        return self.data['name']

    @property
    def dataset(self):
        return self.data['dataset_id']

    @property
    def starred(self):
        return self.data['starred']


class VariablesGroups(EntitiesList):

    id_field = _VARIABLE_GROUP_ID_FIELD
    entity_repo = get_variable_group_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return VariableGroup
