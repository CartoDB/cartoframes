import json
import requests
import shapely

def df_add_geometries(df, properties=['wof_name', 'wof_id','mz_uri']):
    geometries = []
    for i, row in df.iterrows():
        polygon_geometry = json.loads(requests.get(row['mz_uri']).text)
        shape = shapely.geometry.shape(polygon_geometry['geometry'])
        geometries.append(shape)
    df['geometry'] = geometries
    return df
