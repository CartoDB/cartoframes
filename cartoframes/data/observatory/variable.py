from __future__ import absolute_import

from .entity import EntitiesList, SingleEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo

_VARIABLE_ID_FIELD = 'id'


class Variable(SingleEntity):

    id_field = _VARIABLE_ID_FIELD
    entity_repo = get_variable_repo()

    @classmethod
    def _get_entities_list_class(cls):
        return Variables

    def datasets(self):
        return get_dataset_repo().get_by_variable(self._get_id())


class Variables(EntitiesList):

    id_field = _VARIABLE_ID_FIELD
    entity_repo = get_variable_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return Variable
