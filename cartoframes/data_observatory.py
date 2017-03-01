"""Data Observatory methods"""
import json
import pandas as pd
import cartoframes_utils

def read_data_obs(self, hints, debug=False):
    """
    Read metadata from the data observatory
    """

    numerator_query = '''
    SELECT * FROM OBS_GetAvailableNumerators(
        (SELECT ST_SetSRID(ST_Extent(the_geom), 4326)
          FROM {tablename}),
        '{array_of_things}'
    ) numers'''.format(tablename=json.loads(self._metadata[-1])['carto_table'],
                       array_of_things=hints)
    if debug: print(numerator_query)
    resp = self.carto_sql_client.send(numerator_query)
    schema = cartoframes_utils.transform_schema(resp['fields'])
    return pd.DataFrame(resp['rows']).astype(schema)

pd.DataFrame.read_data_obs = read_data_obs
