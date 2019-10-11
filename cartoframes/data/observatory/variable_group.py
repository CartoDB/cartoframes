from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.variable_group_repo import get_variable_group_repo
from .repository.variable_repo import get_variable_repo
from .repository.constants import VARIABLE_GROUP_FILTER


class VariableGroup(CatalogEntity):

    entity_repo = get_variable_group_repo()

    @property
    def variables(self):
        return get_variable_repo().get_all({VARIABLE_GROUP_FILTER: self.id})

    @property
    def name(self):
        return self.data['name']

    @property
    def dataset(self):
        return self.data['dataset_id']

    @property
    def starred(self):
        return self.data['starred']
