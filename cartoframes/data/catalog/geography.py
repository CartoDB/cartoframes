import pandas as pd
from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo

_GEOGRAPHY_FIELD_ID = 'id'


class Geography(pd.Series):

    @property
    def _constructor(self):
        return Geography

    @property
    def _constructor_expanddim(self):
        return Geographies

    @staticmethod
    def get_by_id(geography_id):
        metadata = get_geography_repo().get_by_id(geography_id)
        return Geography(metadata)

    @property
    def datasets(self):
        return get_dataset_repo().get_by_geography(self[_GEOGRAPHY_FIELD_ID])


class Geographies(pd.DataFrame):

    @property
    def _constructor(self):
        return Geographies

    @property
    def _constructor_sliced(self):
        return Geography

    @staticmethod
    def get_all():
        return Geographies([Geography(var) for var in get_geography_repo().get_all()])

    @staticmethod
    def get_by_id(geography_id):
        return Geography.get_by_id(geography_id)
