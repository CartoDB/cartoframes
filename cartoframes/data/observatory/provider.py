from __future__ import absolute_import

from .entity import EntitiesList, SingleEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.provider_repo import get_provider_repo

_PROVIDER_ID_FIELD = 'id'


class Provider(SingleEntity):

    id_field = _PROVIDER_ID_FIELD
    entity_repo = get_provider_repo()

    @classmethod
    def _get_entities_list_class(cls):
        return Providers

    def datasets(self):
        return get_dataset_repo().get_by_provider(self._get_id())


class Providers(EntitiesList):

    id_field = _PROVIDER_ID_FIELD
    entity_repo = get_provider_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return Provider
