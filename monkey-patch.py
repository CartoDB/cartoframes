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


def read_carto(self, username, tablename, api_key=None, include_geom=True,
               limit=None):
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
    api_endpoint = 'https://{username}.carto.com/api/v2/sql?'.format(username=username)
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
    # NOTE: pylint complains that we're accessing a 'protected member
    #       _metadata of a client class' (appending to _metadata only works
    #       with strings, not JSON, so we're serializing here)
    _df._metadata.append(json.dumps({'carto_table': tablename,
                                     'carto_username': username,
                                     'carto_api_key': api_key,
                                     'carto_include_geom': include_geom,
                                     'carto_limit': limit,
                                     'carto_schema': _df.columns}))
    _df.set_index('cartodb_id')
    self.carto_last_state = _df
    return _df

pd.read_carto = read_carto


# TODO: add into update_carto function as subfunction?
def process_item(item):
    from math import isnan
    if isinstance(item, str):
        return '\'{}\''.format(item)
    elif isinstance(item, float):
        if isnan(item):
            return 'null'
        return str(item)
    return str(item)

def datatype_map(dtype):
    if 'float' in dtype:
        return 'numeric'
    elif 'int' in dtype:
        return 'int'
    else:
        return 'text'

# TODO: add check of current schema with metadata schema
#       if new column, do `alter table ... add column ...`
#       if deleted column, do `alter table ... drop column ...
# TODO: make less buggy about the diff between NaNs and nulls
def update_carto(self):
    import urllib
    import json
    import requests
    api_endpoint = 'https://{username}.carto.com/api/v2/sql?'.format(
        username=json.loads(self._metadata[0])['carto_username'])
    if 'carto_api_key' in json.loads(self._metadata[0]):
        params = {
            'api_key': json.loads(self._metadata[0])['carto_api_key']
        }
    else:
        raise Exception("No API key set for this dataframe.")
    # update current state of dataframe
    # diff with the last retrieved version from carto
    filename = 'carto_temp_{}'.format(
        json.loads(self._metadata[0])['carto_table'])
    print filename
    last_state = pd.read_csv(filename, index_col='cartodb_id')
    # print last_state.head()

    # create new column if needed
    if len(last_state.columns) < len(self.columns):
        newcols = set(self.columns) - set(last_state.columns)
        for col in newcols:
            print "Create new column {col}".format(col=col)
            alter_query = '''
                ALTER TABLE {tablename}
                ADD COLUMN {colname} {datatype};
            '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
                       colname=col,
                       datatype=datatype_map(self.dtypes[col]))
            print alter_query
            params['q'] = alter_query
            requests.get(api_endpoint + urllib.urlencode(params))
            for item in self[col].iteritems():
                update_query = '''
                    UPDATE {tablename}
                    SET "{colname}" = {colval}
                    WHERE "cartodb_id" = {cartodb_id}
                '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
                           colname=col,
                           colval=process_item(item[1]),
                           cartodb_id=item[0])
    # drop column if needed
    elif len(last_state.columns) > len(self.columns):
        discardedcols = set(self.columns) - set(last_state.columns)
        for col in discardedcols:
            alter_query = '''

            '''

    # sync updated values
    df_diff = (self != last_state).stack()
    for i in df_diff.iteritems():
        if i[1]:
            print i
            cartodb_id = i[0][0]
            colname = i[0][1]
            upsert_query = '''
            INSERT INTO {tablename}("cartodb_id", "{colname}")
                 VALUES ({cartodb_id}, {colval})
            ON CONFLICT ("cartodb_id")
            DO UPDATE SET "{colname}" = {colval}
            WHERE EXCLUDED."cartodb_id" = {cartodb_id}
            '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
                       colname=colname,
                       colval=process_item(self.loc[cartodb_id][colname]),
                       cartodb_id=cartodb_id)
            print upsert_query
            params['q'] = upsert_query
            resp = requests.get(api_endpoint + urllib.urlencode(params))
            print json.loads(resp.text)
        else:
            continue

pd.DataFrame.update_carto = update_carto
