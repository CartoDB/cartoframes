from .dataset_base import DatasetBase


class DataFrameDataset(DatasetBase):
    def __init__(self, data):
        super(DataFrameDataset, self).__init__(data)
        self._state = DataFrameDataset.STATE_LOCAL

    def download(self):
        raise ValueError('It is not possible to download a DataFrameDataset')

    def upload(self):
        pass
