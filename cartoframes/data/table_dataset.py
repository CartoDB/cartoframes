from .dataset_base import DatasetBase
from ..columns import normalize_name


class TableDataset(DatasetBase):
    def __init__(self, data, context=None, schema=None):
        super(TableDataset, self).__init__(normalize_name(data))
        self._state = DatasetBase.STATE_REMOTE

        if context:
            self._context = context

        self.schema = schema or self._get_schema()
        self._dataset_info = None
        self._normalized_column_names = None

        if self.data != data:
            warn('Table will be named `{}`'.format(table_name))

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
