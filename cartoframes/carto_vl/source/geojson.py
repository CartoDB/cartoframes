from __future__ import absolute_import
from .source import Source
import numpy as np

try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


class GeoJSON(Source):
    """
      TODO
    """

    def __init__(self, data):
        if not HAS_GEOPANDAS:
            raise ValueError(
              """
                GeoJSON source only works with GeoDataFrames from
                the geopandas package http://geopandas.org/data_structures.html#geodataframe
              """)

        if isinstance(data, str):
            source = geopandas.read_file(data)
        elif isinstance(data, geopandas.GeoDataFrame):
            source = data

        filtered_geometries = _filter_null_geometries(source)
        geometries = _set_time_cols_epoc(filtered_geometries)
        query = geometries.to_json()
        _df_nonnull = source[~source.geometry.isna()]
        bounds = _df_nonnull.total_bounds.tolist()

        super(GeoJSON, self).__init__(query, bounds)


def _filter_null_geometries(data):
    return data[~data.geometry.isna()]


def _set_time_cols_epoc(geometries):
    include = ['datetimetz', 'datetime', 'timedelta']

    for column in geometries.select_dtypes(include=include).columns:
        geometries[column] = geometries[column].astype(np.int64)

    return geometries
