from __future__ import absolute_import
import base64
import numpy as np

try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


def load_geojson(geojson):
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

    return data


def get_query_and_bounds(data):
    filtered_geometries = _filter_null_geometries(data)
    bounds = filtered_geometries.total_bounds.tolist()
    data = _set_time_cols_epoc(filtered_geometries).to_json()
    query = base64.b64encode(data.encode('utf-8')).decode('utf-8')

    return query, bounds

def _filter_null_geometries(data):
    return data[~data.geometry.isna()]


def _set_time_cols_epoc(geometries):
    include = ['datetimetz', 'datetime', 'timedelta']

    for column in geometries.select_dtypes(include=include).columns:
        geometries[column] = geometries[column].astype(np.int64)

    return geometries
