from pandas import DataFrame

from .context_manager import ContextManager


class SourceManager(object):

    def __init__(self, source, credentials):
        if isinstance(source, str):
            # Table, SQL query
            self._remote_data = True
            self._context_manager = ContextManager(credentials)
            self._query = self._context_manager.compute_query(source)
        elif isinstance(source, DataFrame):
            # DataFrame, GeoDataFrame, CartoDataFrame
            self._remote_data = False
            self._df = source
        else:
            raise ValueError('Wrong source input. Valid values are str and DataFrame.')

    def is_remote(self):
        return self._remote_data

    def is_local(self):
        return not self._remote_data

    def get_query(self):
        if self.is_remote():
            return self._query

    def get_num_rows(self):
        if self.is_remote():
            return self._context_manager.get_num_rows(self._query)
        else:
            return len(self._df)

    def get_column_names(self):
        if self.is_remote():
            return self._context_manager.get_column_names(self._query)
        else:
            return list(self._df.columns)
