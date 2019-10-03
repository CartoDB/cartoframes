import pandas as pd

try:
    from abc import ABC, abstractmethod
except ImportError:
    from abc import ABCMeta, abstractmethod
    ABC = ABCMeta('ABC', (object,), {'__slots__': ()})


class CatalogEntity(ABC):

    id_field = None
    entity_repo = None

    def __init__(self, data):
        self.data = data

    @classmethod
    def get(cls, id_):
        return cls.entity_repo.get_by_id(id_)

    @classmethod
    def get_all(cls):
        return cls.entity_repo.get_all()

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return not self == other


class SingleEntity(CatalogEntity, ABC):

    @property
    def id(self):
        return self.data[self.id_field]

    def to_series(self):
        return pd.Series(self.data)

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.data.__repr__()


class EntitiesList(list, CatalogEntity, ABC):

    def __init__(self, data):
        super(EntitiesList, self).__init__(data)
        self.data = data

    def __getitem__(self, y):
        item = list.__getitem__(self, y)
        return self._get_single_entity_class()(item)

    def __iter__(self):
        return (self._get_single_entity_class()(item) for item in list.__iter__(self))

    @classmethod
    @abstractmethod
    def _get_single_entity_class(cls):
        raise NotImplementedError

    def to_dataframe(self):
        return pd.DataFrame(self.data)
