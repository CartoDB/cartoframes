import pandas as pd
from .repository.dataset_repo import get_dataset_repo


class Dataset(pd.Series):

    @property
    def _constructor(self):
        return Dataset

    @property
    def _constructor_expanddim(self):
        return Datasets

    @staticmethod
    def get_by_id(dataset_id):
        dataset = get_dataset_repo().get_by_id(dataset_id)
        return Dataset(dataset)


class Datasets(pd.DataFrame):

    @property
    def _constructor(self):
        return Datasets

    @property
    def _constructor_sliced(self):
        return Dataset

    @staticmethod
    def get_all():
        return Datasets([Dataset(dataset) for dataset in get_dataset_repo().get_all()])

    @staticmethod
    def get_by_id(dataset_id):
        return Dataset.get_by_id(dataset_id)
