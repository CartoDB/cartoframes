from .entity import SingleEntity, EntitiesList
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo
from .repository.variable_group_repo import get_variable_group_repo

_DATASET_ID_FIELD = 'id'


class Dataset(SingleEntity):

    id_field = _DATASET_ID_FIELD
    entity_repo = get_dataset_repo()

    def variables(self):
        return get_variable_repo().get_by_dataset(self.id)

    def variables_groups(self):
        return get_variable_group_repo().get_by_dataset(self.id)

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
    def country(self):
        return self.data['country_iso_code3']

    @property
    def category(self):
        return self.data['category_id']


class Datasets(EntitiesList):

    id_field = _DATASET_ID_FIELD
    entity_repo = get_dataset_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return Dataset
