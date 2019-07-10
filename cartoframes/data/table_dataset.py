from .dataset_base import DatasetBase


class TableDataset(DatasetBase):
    def __init__(self, data, context=None, schema=None):
        super(TableDataset, self).__init__(data)
        self._state = DataFrameDataset.STATE_REMOTE

        if context:
            self._context = context

        self.schema = schema or self._get_schema()
        self._dataset_info = None

    def download(self):
        pass

    def upload(self):
        raise ValueError('It is not possible to upload a TableDataset')

    @property
    def dataset_info(self):
        if self._dataset_info is None:
            self._dataset_info = self._get_dataset_info()

        return self._dataset_info

    def update_dataset_info(self, privacy=None, name=None):
        self._dataset_info = self.dataset_info
        self._dataset_info.update(privacy=privacy, name=name)
