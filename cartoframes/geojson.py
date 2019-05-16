from __future__ import absolute_import

import base64
import numpy as np

try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


def load_geojson(input_data):
    if not HAS_GEOPANDAS:
        raise ValueError(
            """
            GeoJSON source only works with GeoDataFrames from
            the geopandas package http://geopandas.org/data_structures.html#geodataframe
            """)

    if isinstance(input_data, str):
        # File name
        data = geopandas.read_file(input_data)

    elif isinstance(input_data, list):
        # List of features
        data = geopandas.GeoDataFrame.from_features(input_data)

    elif isinstance(input_data, dict):
        # GeoJSON object
        if input_data.get('features'):
            # From features
            data = geopandas.GeoDataFrame.from_features(input_data['features'])
        elif input_data.get('type') == 'Feature':
            # From feature
            data = geopandas.GeoDataFrame.from_features([input_data])
        elif input_data.get('type'):
            # From geometry
            data = geopandas.GeoDataFrame.from_features([{
                'type': 'Feature',
                'properties': {},
                'geometry': input_data
            }])

    elif isinstance(input_data, geopandas.GeoDataFrame):
        # GeoDataFrame
        data = geopandas.GeoDataFrame.from_features(input_data)

    else:
        raise ValueError(
            """
            GeoJSON source only works with GeoDataFrames from
            the geopandas package http://geopandas.org/data_structures.html#geodataframe
            """)

    return data


def get_encoded_data(data):
    filtered_geometries = _filter_null_geometries(data)
    data = _set_time_cols_epoc(filtered_geometries).to_json()
    encoded_data = base64.b64encode(data.encode('utf-8')).decode('utf-8')

    return encoded_data


def get_bounds(data):
    filtered_geometries = _filter_null_geometries(data)
    bounds = filtered_geometries.total_bounds.tolist()

    return bounds


def _filter_null_geometries(data):
    return data[~data.geometry.isna()]


def _set_time_cols_epoc(geometries):
    include = ['datetimetz', 'datetime', 'timedelta']

    for column in geometries.select_dtypes(include=include).columns:
        geometries[column] = geometries[column].astype(np.int64)

    return geometries
