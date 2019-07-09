from .dataset_base import DatasetBase


class QueryDataset(DatasetBase):
    def __init__(self, data, context):
        super(QueryDataset, self).__init__(data)
        self._state = DataFrameDataset.STATE_REMOTE
        self._is_saved_in_carto = True

        if context:
            self._context = context


    def download(self):
        pass

    def upload(self):
        pass
