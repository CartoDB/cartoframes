from .entity import EntitiesList, SingleEntity
from .repository.geography_repo import get_geography_repo
from .repository.country_repo import get_country_repo
from .repository.dataset_repo import get_dataset_repo

_COUNTRY_ID_FIELD = 'country_iso_code3'


class Country(SingleEntity):

    id_field = _COUNTRY_ID_FIELD
    entity_repo = get_country_repo()

    def datasets(self):
        return get_dataset_repo().get_by_country(self._get_id())

    def geographies(self):
        return get_geography_repo().get_by_country(self._get_id())

    @classmethod
    def _get_entities_list_class(cls):
        return Countries


class Countries(EntitiesList):

    id_field = _COUNTRY_ID_FIELD
    entity_repo = get_country_repo()

    def __init__(self, data):
        super(Countries, self).__init__(data)
        self._use_id_as_index()

    @classmethod
    def _get_single_entity_class(cls):
        return Country
