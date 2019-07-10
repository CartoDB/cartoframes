from .dataset_base import DatasetBase


class QueryDataset(DatasetBase):
    def __init__(self, data, context):
        super(QueryDataset, self).__init__(data)
        self._state = DatasetBase.STATE_REMOTE

        if context:
            self._context = context


    def download(self):
        pass

    def upload(self):
        pass
