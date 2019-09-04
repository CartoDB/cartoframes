import pandas as pd
from .repository.dataset_repo import get_dataset_repo


class Dataset(pd.Series):

    def __init__(self, dataset):
        super(Dataset, self).__init__(dataset)

    @staticmethod
    def get_by_id(dataset_id):
        dataset = get_dataset_repo().get_by_id(dataset_id)
        return Dataset(dataset)


class Datasets(pd.DataFrame):
    def __init__(self, items):
        super(Datasets, self).__init__(items)

    @staticmethod
    def get_all():
        return Datasets([Dataset(dataset) for dataset in get_dataset_repo().get_all()])

    @staticmethod
    def get_by_id(dataset_id):
        return Dataset.get_by_id(dataset_id)
