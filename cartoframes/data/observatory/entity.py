import pandas as pd

from cartoframes.exceptions import DiscoveryException

try:
    from abc import ABC, abstractmethod
except ImportError:
    from abc import ABCMeta, abstractmethod
    ABC = ABCMeta('ABC', (object,), {'__slots__': ()})


class CatalogEntity(ABC):

    id_field = None
    entity_repo = None

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
        return cls.entity_repo.get_by_id(id_)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other


class SingleEntity(CatalogEntity, pd.Series, ABC):

    @property
    def _constructor_expanddim(self):
        return self._get_entities_list_class()

    @classmethod
    def _get_single_entity_class(cls):
        return cls

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
        self.set_index(self.id_field, inplace=True, drop=False)

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
    def _get_entities_list_class(cls):
        return cls

    @classmethod
    def get_all(cls):
        return cls.entity_repo.get_all()
