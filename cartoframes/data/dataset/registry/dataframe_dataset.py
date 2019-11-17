from __future__ import absolute_import

from tqdm import tqdm

from .base_dataset import BaseDataset

# avoid _lock issue: https://github.com/tqdm/tqdm/issues/457
tqdm(disable=True, total=0)  # initialise internal lock


class DataFrameDataset(BaseDataset):
    def __init__(self, data, credentials=None, schema=None):
        pass

    def get_column_names(self, exclude=None):
        """Get column names"""
        columns = list(self.dataframe.columns)
        if self.dataframe.index.name is not None and self.dataframe.index.name not in columns:
            columns.append(self.dataframe.index.name)

        if exclude and isinstance(exclude, list):
            columns = list(set(columns) - set(exclude))

        return columns

    def _rename_index_for_upload(self):
        if self._df.index.name != 'cartodb_id':
            if 'cartodb_id' not in self._df:
                if _is_valid_index_for_cartodb_id(self._df.index):
                    # rename a integer unnamed index to cartodb_id
                    self._df.index.rename('cartodb_id', inplace=True)
            else:
                if self._df.index.name is None:
                    # replace an unnamed index by a cartodb_id column
                    self._df.set_index('cartodb_id')


def _is_valid_index_for_cartodb_id(index):
    return index.name is None and index.nlevels == 1 and index.dtype == 'int' and index.is_unique
