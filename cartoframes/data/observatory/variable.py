from .entity import SingleEntity, EntitiesList
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo

_VARIABLE_ID_FIELD = 'id'


class Variable(SingleEntity):

    id_field = _VARIABLE_ID_FIELD
    entity_repo = get_variable_repo()

    def datasets(self):
        return get_dataset_repo().get_by_variable(self.id)

    @property
    def id(self):
        return self.data[self.id_field]

    @property
    def name(self):
        return self.data['name']

    @property
    def description(self):
        return self.data['description']

    @property
    def starred(self):
        return self.data['starred']


class Variables(EntitiesList):

    id_field = _VARIABLE_ID_FIELD
    entity_repo = get_variable_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return Variable
