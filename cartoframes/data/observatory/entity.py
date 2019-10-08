import pandas as pd

try:
    from abc import ABC
except ImportError:
    from abc import ABCMeta
    ABC = ABCMeta('ABC', (object,), {'__slots__': ()})


class CatalogEntity(ABC):

    id_field = 'id'
    entity_repo = None

    def __init__(self, data):
        self.data = data

    @property
    def id(self):
        return self.data[self.id_field]

    @classmethod
    def get(cls, id_):
        return cls.entity_repo.get_by_id(id_)

    @classmethod
    def get_all(cls):
        return cls.entity_repo.get_all()

    def to_series(self):
        return pd.Series(self.data)

    def to_dict(self):
        return self.data

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '{classname}({data})'.format(classname=self.__class__.__name__, data=self.data.__str__())

    def __repr__(self):
        return '{classname}({entity_id})'.format(classname=self.__class__.__name__, entity_id=self.id)


class CatalogList(list):

    def __init__(self, data):
        super(CatalogList, self).__init__(data)

    def get(self, item_id):
        return next(filter(lambda item: item.id == item_id, self), None)

    def to_dataframe(self):
        return pd.DataFrame([item.data for item in self])
