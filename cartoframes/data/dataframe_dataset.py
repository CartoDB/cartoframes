from .dataset_base import DatasetBase


class DataFrameDataset(DatasetBase):
    def __init__(self, data):
        super(DataFrameDataset, self).__init__(data)
        self._state = DataFrameDataset.STATE_LOCAL
        self._is_saved_in_carto = False

    def download(self):
        pass

    def upload(self):
        pass
