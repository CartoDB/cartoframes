# -*- coding: utf-8 -*-

import pandas as pd

from cartoframes.dataset import Dataset


class MetadataMock():
    def __init__(self):
        self.privacy = 'PRIVATE'

    def save(self):
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

    def _get_metadata(self):
        if self._is_saved_in_carto:
            self._metadata = MetadataMock()
            return True
        else:
            return False
