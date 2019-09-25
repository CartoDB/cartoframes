import pandas as pd

from abc import ABC
from cartoframes.exceptions import DiscoveryException


class CatalogEntity(ABC):

    id_field = None
    entity_repo = None

    @classmethod
    def _get_single_entity_class(cls):
        return cls

    @classmethod
    def _get_entities_list_class(cls):
        return cls

    @classmethod
    def get_by_id(cls, id_):
        return cls.entity_repo.get_by_id(id_)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other


class SingleEntity(CatalogEntity, pd.Series, ABC):

    @property
    def _constructor_expanddim(self):
        return self._get_entities_list_class()

    def _get_id(self):
        try:
            return self[self.id_field]
        except KeyError:
            raise DiscoveryException('Unsupported function: this instance actually represents a subset of entities.'
                                     ' You should use the method `get_by_id("id")` to obtain a valid '
                                     'instance of the class and then attempt this function on it.')


class EntitiesList(CatalogEntity, pd.DataFrame, ABC):

    def __init__(self, data):
        super(EntitiesList, self).__init__(data)
        self._use_id_as_index()

    @property
    def _constructor(self):
        return self.__class__

    @property
    def _constructor_sliced(self):
        return self._get_single_entity_class()

    @property
    def _constructor_expanddim(self):
        return self.__class__

    @classmethod
    def get_all(cls):
        return cls.entity_repo.get_all()

    def _use_id_as_index(self):
        self.set_index(self.id_field, inplace=True, drop=False)
