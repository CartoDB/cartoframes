"""
Monkey patching pandas to add utilities for CARTO tables
Andy Eschbacher and Stuart Lynn, 2017

Project goals
    * Like geopandas, have a .cartomap() method which gives back the data
      as a map using carto's maps api and turbocartocss on an optional
      attribute

Features to add:
    * create a dataframe from scratch
        * establish cartodb_id
        * set metadata manually
        * register with carto

Notes on propagating pandas metadata:
    * https://github.com/pandas-dev/pandas/issues/2485
    * geopandas does a good job of propagating metadata, seems to be by
      subclassing Dataframes:
      https://github.com/geopandas/geopandas/blob/v0.2.1/geopandas/geodataframe.py#L54
      similar to what we tried in cartopandas.py.
      A geodataframe stores it's own metadata:
      https://github.com/geopandas/geopandas/blob/v0.2.1/geopandas/geodataframe.py#L47
"""

# TODO: hook into pandas.core?
import pandas as pd

def add_meta(self, **kwargs):
    """
        Set metadata for a dataframe if none has been already set
    """
    for key in kwargs:
        self._metadata[0][key] = kwargs[key]


def read_carto(username, tablename, api_key=None, include_geom=True,
               include_date_util=False, limit=None):
    """Import a table from carto into a pandas dataframe, storing
       table information in pandas metadata"""
    import json
    from urllib import urlencode

    # construct query
    query = 'SELECT * FROM {tablename}'.format(tablename=tablename)
    if limit:
        if (limit >= 0) and isinstance(limit, int):
            query += ' LIMIT {limit}'.format(limit=limit)
        else:
            raise ValueError("limit parameter must an integer >= 0")
    # print query
    
    # construct API call
    api_endpoint = 'https://{}.carto.com/api/v2/sql?'.format(username)
    # add parameters
    params = {'format': 'csv',
              'q': query}
    # API key if passed
    if api_key:
        params['api_key'] = api_key
    # exclude geometry columns if asked
    if not include_geom:
        params['skipfields'] = 'the_geom,the_geom_webmercator'
    print api_endpoint + urlencode(params)
    _df = pd.read_csv(api_endpoint + urlencode(params))
    # TODO: add table schema to the metadata
    # NOTE: pylint complaints that we're accessing a 'protected member
    #       _metadata of a client class'
    # TODO: see how geopandas does it
    _df._metadata.append(json.dumps({'carto_table': tablename,
                                     'carto_username': username,
                                     'carto_api_key': api_key,
                                     'carto_include_geom': include_geom,
                                     'carto_limit': limit}))
    return _df.set_index('cartodb_id')

pd.read_carto = read_carto


# TODO: add into update_carto funciton as subfunction?
def process_item(item):
    from math import isnan
    if isinstance(item, str):
        return '\'{}\''.format(item)
    elif isinstance(item, float):
        if isnan(item):
            return 'null'
        return str(item)
    return str(item)


# TODO: add check of current schema with metadata schema
#       if new column, do `alter table ... add column ...`
#       if deleted column, do `alter table ... drop column ... `
def update_carto(self):
    import requests
    from urllib import urlencode
    api_endpoint = 'https://{}.carto.com/api/v2/sql?'.format(
        json.loads(self._metadata[0])['carto_username'])
    if 'api_key' in json.loads(self._metadata[0]):
        params = {
            'api_key': json.loads(self._metadata[0])['api_key']
        }
    else:
        raise Exception("No API key set for this dataframe.")
    for row in self.iterrows():
        cartodb_id = row[0]
        key_vals = zip(['"{}"'.format(c) for c in self.columns], row[1].values)
        setcols = ', '.join(["{col} = {val}".format(col=kv[0],
                                                    val=process_item(kv[1]))
                             for kv in key_vals])

        update_query = '''
        UPDATE {tablename}
        SET {col_exprs}
        WHERE cartodb_id = {cartodb_id}
        '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
                   col_exprs=setcols,
                   cartodb_id=cartodb_id)
        params['q'] = update_query
        # print update_query
        resp = requests.get(api_endpoint + urlencode(params))
        print resp.text
        # TODO: return the status of all of the updates

pd.DataFrame.update_carto = update_carto


