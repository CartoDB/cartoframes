import pandas as pd
from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo


class Geography(pd.Series):

    def __init__(self, geography):
        super(Geography, self).__init__(geography)

    @staticmethod
    def get_by_id(geography_id):
        metadata = get_geography_repo().get_by_id(geography_id)
        return Geography(metadata)

    @property
    def datasets(self):
        return get_dataset_repo().get_by_geography(self.id)


class Geographies(pd.DataFrame):

    def __init__(self, items):
        super(Geographies, self).__init__(items)

    @staticmethod
    def get_all():
        return Geographies([Geography(var) for var in get_geography_repo().get_all()])

    @staticmethod
    def get_by_id(geography_id):
        return Geography.get_by_id(geography_id)
