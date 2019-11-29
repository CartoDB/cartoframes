from pandas import DataFrame

from .context_manager import ContextManager
from ..cartodataframe import CartoDataFrame
from ...utils.utils import is_sql_query


class SourceManager(object):

    def __init__(self, source, credentials):
        self._source = source
        if isinstance(source, str):
            # Table, SQL query
            self._remote_data = True
            self._context_manager = ContextManager(credentials)
            self._query = self._context_manager.compute_query(source)
        elif isinstance(source, DataFrame):
            # DataFrame, GeoDataFrame, CartoDataFrame
            self._remote_data = False
            self._cdf = CartoDataFrame(source, copy=True)
        else:
            raise ValueError('Wrong source input. Valid values are str and DataFrame.')

    @property
    def cdf(self):
        return self._cdf

    def is_remote(self):
        return self._remote_data

    def is_local(self):
        return not self._remote_data

    def is_table(self):
        return isinstance(self._source, str) and not self.is_query()

    def is_query(self):
        return is_sql_query(self._source)

    def is_dataframe(self):
        return isinstance(self._source, DataFrame)

    def get_query(self):
        if self.is_remote():
            return self._query

    def get_num_rows(self):
        if self.is_remote():
            return self._context_manager.get_num_rows(self._query)
        else:
            return len(self._cdf)

    def get_column_names(self):
        if self.is_remote():
            return self._context_manager.get_column_names(self._query)
        else:
            return list(self._cdf.columns)
