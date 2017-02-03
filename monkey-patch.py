"""
Monkey patching pandas to add utilities for CARTO tables
"""

# TODO: hook into pandas.core?
import pandas

def read_carto(username, tablename, api_key=None, include_geom=True,
               include_date_util=False, limit=None):
    """Import a table from carto into a pandas dataframe, storing
       table information in pandas metadata"""
    import json
    from urllib import urlencode
    # construct query
    query = 'SELECT * FROM {tablename}'.format(tablename=tablename)
    if limit:
        if (limit >= 0) and (type(limit) == int):
            query += ' LIMIT {limit}'.format(limit=limit)
        else:
            raise ValueError("limit parameter must an integer >= 0")
    print query
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
    _df._metadata.append(json.dumps({'carto_table': tablename,
                                     'carto_username': username,
                                     'carto_api_key': api_key,
                                     'carto_include_geom': include_geom,
                                     'carto_limit': limit}))
    return _df.set_index('cartodb_id')

pd.read_carto = read_carto

def update_carto(self):
    import requests
    api_endpoint = 'https://{}.carto.com/api/v2/sql?'.format(
        json.loads(self._metadata[0])['carto_username'])
    params = {
        'api_key': APIKEY
    }
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
        # print resp.text
        # TODO: return the status of all of the updates

pd.DataFrame.update_carto = update_carto


