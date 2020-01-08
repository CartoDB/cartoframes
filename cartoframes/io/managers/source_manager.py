from pandas import DataFrame
from geopandas import GeoDataFrame

from .context_manager import ContextManager
from ...utils.utils import is_sql_query
from ...utils.geom_utils import has_geometry


class SourceManager:

    def __init__(self, source, credentials):
        self._source = source
        if isinstance(source, str):
            # Table, SQL query
            self._remote_data = True
            self._context_manager = ContextManager(credentials)
            self._query = self._context_manager.compute_query(source)
        elif isinstance(source, DataFrame):
            # DataFrame, GeoDataFrame
            self._remote_data = False
            self._gdf = GeoDataFrame(source, copy=True)
            if has_geometry(source):
                self._gdf.set_geometry(source.geometry.name, inplace=True)
        else:
            raise ValueError('Wrong source input. Valid values are str and DataFrame.')

    @property
    def gdf(self):
        return self._gdf

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
            return len(self._gdf)

    def get_column_names(self):
        if self.is_remote():
            return self._context_manager.get_column_names(self._query)
        else:
            return list(self._gdf.columns)
