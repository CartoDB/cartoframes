import pandas as pd

from abc import ABC, abstractmethod
from cartoframes.exceptions import DiscoveryException


class CatalogEntity(ABC):

    @classmethod
    @abstractmethod
    def _get_id_field(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _get_entity_repo(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _get_single_entity_class(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _get_entities_list_class(cls):
        raise NotImplementedError

    @classmethod
    def get_by_id(cls, id_):
        return cls._get_entity_repo().get_by_id(id_)

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
            return self[self._get_id_field()]
        except KeyError:
            raise DiscoveryException('Unsupported function: this instance actually represents a subset of entities.'
                                     ' You should use the method `get_by_id("id")` to obtain a valid '
                                     'instance of the class and then attempt this function on it.')

    def __eq__(self, other):
        return self.equals(other)


class EntitiesList(CatalogEntity, pd.DataFrame, ABC):

    @property
    def _constructor(self):
        return self._get_entities_list_class()

    @property
    def _constructor_sliced(self):
        return self._get_single_entity_class()

    @property
    def _constructor_expanddim(self):
        return self._get_entities_list_class()

    @classmethod
    def get_all(cls):
        return cls._get_entity_repo().get_all()

    def _set_index(self):
        self.set_index(self._get_id_field(), inplace=True, drop=False)
