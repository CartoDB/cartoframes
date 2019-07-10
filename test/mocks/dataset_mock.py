# -*- coding: utf-8 -*-

import pandas as pd

from cartoframes.data import Dataset, DatasetInfo


class MetadataMock():
    def __init__(self):
        self.privacy = DatasetInfo.PRIVATE
        self.name = None


class DatasetInfoMock(DatasetInfo):
    def _get_metadata(self, _1, _2):
        return MetadataMock()

    def _save_metadata(self):
        return True


class DatasetMock(Dataset):
    def download(self):
        self._df = pd.DataFrame({'column_name': [1]})
        return self._df

    def _copyfrom(self, _):
        return True

    def _create_table(self, _):
        return True

    def _create_table_from_query(self):
        return True

    def exists(self):
        return False

    def _get_dataset_info(self):
        return DatasetInfoMock(self._con, self._table_name)

    def compute_geom_type(self):
        return Dataset.GEOM_TYPE_POINT

    def _create_client(self):
        return None
