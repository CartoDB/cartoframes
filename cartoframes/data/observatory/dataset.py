from __future__ import absolute_import

from .entity import SingleEntity, EntitiesList
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo
from .repository.variable_group_repo import get_variable_group_repo

_DATASET_ID_FIELD = 'id'


class Dataset(SingleEntity):

    id_field = _DATASET_ID_FIELD
    entity_repo = get_dataset_repo()

    @classmethod
    def _get_entities_list_class(cls):
        return Datasets

    def variables(self):
        return get_variable_repo().get_by_dataset(self._get_id())

    def variables_groups(self):
        return get_variable_group_repo().get_by_dataset(self._get_id())


class Datasets(EntitiesList):

    id_field = _DATASET_ID_FIELD
    entity_repo = get_dataset_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return Dataset
