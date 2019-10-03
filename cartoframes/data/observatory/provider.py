from __future__ import absolute_import

from .entity import SingleEntity, EntitiesList
from .repository.provider_repo import get_provider_repo
from .repository.dataset_repo import get_dataset_repo


_PROVIDER_ID_FIELD = 'id'


class Provider(SingleEntity):

    id_field = _PROVIDER_ID_FIELD
    entity_repo = get_provider_repo()

    def datasets(self):
        return get_dataset_repo().get_by_provider(self.id)

    @property
    def id(self):
        return self.data[self.id_field]

    @property
    def name(self):
        return self.data['name']


class Providers(EntitiesList):

    id_field = _PROVIDER_ID_FIELD
    entity_repo = get_provider_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return Provider
