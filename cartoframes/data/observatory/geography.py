from __future__ import absolute_import

from .entity import EntitiesList, SingleEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo

_GEOGRAPHY_ID_FIELD = 'id'


class Geography(SingleEntity):

    id_field = _GEOGRAPHY_ID_FIELD
    entity_repo = get_geography_repo()

    @classmethod
    def _get_entities_list_class(cls):
        return Geographies

    def datasets(self):
        return get_dataset_repo().get_by_geography(self._get_id())


class Geographies(EntitiesList):

    id_field = _GEOGRAPHY_ID_FIELD
    entity_repo = get_geography_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return Geography
