from __future__ import absolute_import
from .source import Source
from .source_types import SourceTypes
import numpy as np

try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


class GeoJSON(Source):
    """Source that parses a GeoJSON

        Args:
            geojson (DataFrame, str): The geojson argument can be a string that refers to the
                GeoJSON file or a geopandas GeoDataFrame

        Example:

            .. code::
                from cartoframes import carto_vl as vl

                vl.Map([
                    vl.Layer(
                        vl.source.GeoJSON('points.geojson')
                    )]
                )
    """

    source_type = SourceTypes.GeoJSON

    def __init__(self, geojson):
        if not HAS_GEOPANDAS:
            raise ValueError(
              """
                GeoJSON source only works with GeoDataFrames from
                the geopandas package http://geopandas.org/data_structures.html#geodataframe
              """)

        if isinstance(geojson, str):
            data = geopandas.read_file(geojson)
        elif isinstance(geojson, geopandas.GeoDataFrame):
            data = geopandas.GeoDataFrame.from_features(geojson)
        else:
            raise ValueError(
              """
                GeoJSON source only works with GeoDataFrames from
                the geopandas package http://geopandas.org/data_structures.html#geodataframe
              """)

        filtered_geometries = _filter_null_geometries(data)
        bounds = filtered_geometries.total_bounds.tolist()
        query = _set_time_cols_epoc(filtered_geometries).to_json()

        super(GeoJSON, self).__init__(query, bounds)


def _filter_null_geometries(data):
    return data[~data.geometry.isna()]


def _set_time_cols_epoc(geometries):
    include = ['datetimetz', 'datetime', 'timedelta']

    for column in geometries.select_dtypes(include=include).columns:
        geometries[column] = geometries[column].astype(np.int64)

    return geometries
