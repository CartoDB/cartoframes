"""
Monkey patching pandas to add utilities for CARTO tables and maps
Andy Eschbacher and Stuart Lynn, 2017

Project goals
    * Interact with a CARTO table fully within a Jupyter notebook/pandas
      workflow (read and sync dataframe changes)
    * Like geopandas, have a .carto_map() method which gives back the data
      as a map using carto's maps api and turbocartocss on an optional
      attribute
    * Add CARTO services like the Data Observatory as methods to a dataframe

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
import cartodb

# not currently used
def add_meta(self, **kwargs):
    """
        Set metadata for a dataframe if none has been already set
    """
    for key in kwargs:
        self._metadata[0][key] = kwargs[key]

def map_dtypes(pgtype):
    """
        Map PostgreSQL data types to NumPy/pandas dtypes
    """
    dtypes = {'number': 'float64',
              'date': 'datetime64',
              'string': 'string',
              'geometry': 'string',
              'boolean': 'bool'}
    return dtypes[pgtype]

def transform_schema(pgschema):
    """
        Transform schema returned via SQL API to dict for pandas
    """
    datatypes = {}
    for field in pgschema:
        if 'cartodb_id' in field:
            continue
        datatypes[field] = map_dtypes(pgschema[field]['type'])
    return datatypes

def get_geom_type(sql_auth_client, tablename):
    """
        Get the geometry type in tablename for storing in
        dataframe metadata
    """
    geomtypes = {'ST_Point': 'point',
                 'ST_MultiPoint': 'point',
                 'ST_LineString': 'line',
                 'ST_MultiLineString': 'line',
                 'ST_Polygon': 'polygon',
                 'ST_MultiPolygon': 'polygon'}

    result = sql_auth_client.send('''
        SELECT ST_GeometryType(the_geom) As geomtype
        FROM "{tablename}"
        LIMIT 1'''.format(tablename=tablename))['rows'][0]['geomtype']

    return geomtypes[result]

# NOTE: this is compatible with v1.0.0 of carto-python client
# TODO: remove username as a param would be nice.. accessible to write to
#       metadata from carto python client?
def read_carto(cdb_client, username=None, tablename=None,
               custom_query=None, include_geom=True,
               limit=None, index='cartodb_id', debug=False):
    """Import a table from carto into a pandas dataframe, storing
       table information in pandas metadata"""
    from carto.sql import SQLClient
    import json
    sql = SQLClient(cdb_client)

    # construct query
    if tablename:
        query = 'SELECT * FROM "{tablename}"'.format(tablename=tablename)
        geomtype = get_geom_type(sql, tablename)
        # Add limit if requested
        if limit:
            # NOTE: what if limit is `all` or `none`?
            if (limit >= 0) and isinstance(limit, int):
                query += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")
    elif query:
        # NOTE: note yet implemented
        # query = custom_query
        pass
    else:
        raise NameError("`tablename` or `query` needs to be specified")

    if debug:
        print query

    # exclude geometry columns if asked
    # TODO: include_geom in cdb_client structure?

    if debug:
        print query
    # TODO: how to handle NaNs deterministically?
    resp = sql.send(query)
    schema = transform_schema(resp['fields'])
    _df = pd.DataFrame(resp['rows']).set_index(index).astype(schema)

    # TODO: add table schema to the metadata
    # NOTE: pylint complains that we're accessing a 'protected member
    #       _metadata of a client class' (appending to _metadata only works
    #       with strings, not JSON, so we're serializing here)
    _df._metadata.append(json.dumps({'carto_table': tablename,
                                     'carto_username': username,
                                     'carto_api_key': api_key,
                                     'carto_include_geom': include_geom,
                                     'carto_limit': limit,
                                     'carto_schema': str(schema),
                                     'carto_geomtype': geomtype}))
    _df.carto_last_state = _df.copy(deep=True)
    _df.carto_sql_client = sql
    return _df

pd.read_carto = read_carto


# TODO: add into update_carto function as subfunction?
def process_item(item):
    """
      Map NumPy values to PostgreSQL values
    """
    from math import isnan
    if isinstance(item, str):
        return '\'{}\''.format(item)
    elif isinstance(item, float):
        if isnan(item):
            return 'null'
        return str(item)
    return str(item)

def datatype_map(dtype):
    """
       map NumPy types to PostgreSQL types
    """
    if 'float' in dtype:
        return 'numeric'
    elif 'int' in dtype:
        return 'int'
    else:
        return 'text'

# TODO: make less buggy about the diff between NaNs and nulls
# TODO: batch UPDATES into a transaction
# TODO: if table metadata doesn't exist, error saying need to set 'create'
#       flag
def update_carto(self, createtable=False, debug=False):
    import json
    if createtable is True:
        # TODO: build this
        # grab df schema, setup table, cartodbfy, then exit
        pass
    elif not hasattr(self, 'carto_sql_client'):
        raise Exception("Table not registered with CARTO. Set `createtable` "
                        "flag to True")

    # create new column if needed
    # TODO: extract to function
    if len(set(self.columns) - set(self.carto_last_state.columns)) > 0:
        newcols = set(self.columns) - set(self.carto_last_state.columns)
        for col in newcols:
            if debug: print "Create new column {col}".format(col=col)
            alter_query = '''
                ALTER TABLE "{tablename}"
                ADD COLUMN "{colname}" {datatype}
            '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
                       colname=col,
                       datatype=datatype_map(str(self.dtypes[col])))
            if debug: print alter_query
            # add column
            resp = self.carto_sql_client.send(alter_query)
            # update all the values in that column
            # NOTE: fails if colval is 'inf' or some other Python or NumPy type
            for item in self[col].iteritems():
                if debug: print item
                update_query = '''
                    UPDATE "{tablename}"
                    SET "{colname}" = {colval}
                    WHERE "cartodb_id" = {cartodb_id};
                '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
                           colname=col,
                           colval=process_item(item[1]),
                           cartodb_id=item[0])
                if debug: print update_query
                resp = self.carto_sql_client.send(update_query)
                # if debug: print resp.text
    # drop column if needed
    # TODO: extract to function
    if len(set(self.carto_last_state.columns) - set(self.columns)) > 0:
        discardedcols = set(self.carto_last_state.columns) - set(self.columns)
        for col in discardedcols:
            alter_query = '''
                ALTER TABLE "{tablename}"
                DROP COLUMN "{colname}"
            '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
                       colname=col)

            if debug: print alter_query
            resp = self.carto_sql_client.send(alter_query)
    # sync updated values
    # TODO: extract to functon
    common_cols = list(set(self.columns) & set(self.carto_last_state.columns))
    df_diff = (self[common_cols] != self.carto_last_state[common_cols]).stack()
    for i in df_diff.iteritems():
        # TODO: instead of doing row by row, build up a list of queries
        #       testing to be sure the num of characters is lower than
        #       16368ish. And then run the query as a transaction
        if i[1]:
            if debug: print i
            cartodb_id = i[0][0]
            colname = i[0][1]
            upsert_query = '''
            INSERT INTO "{tablename}"("cartodb_id", "{colname}")
                 VALUES ({cartodb_id}, {colval})
            ON CONFLICT ("cartodb_id")
            DO UPDATE SET "{colname}" = {colval}
            WHERE EXCLUDED."cartodb_id" = {cartodb_id}
            '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
                       colname=colname,
                       colval=process_item(self.loc[cartodb_id][colname]),
                       cartodb_id=cartodb_id)
            if debug: print upsert_query
            resp = self.carto_sql_client.send(upsert_query)
            if debug: print json.loads(resp.text)
        else:
            continue
    # update state of dataframe
    self.carto_last_state = self.copy(deep=True)

pd.DataFrame.update_carto = update_carto


def carto_map(self, interactive=True, stylecol=None):
    """
        Produce and return CARTO maps or iframe embeds
    """
    import urllib
    import json
    try:
        import IPython
        return_iframe = False
    except ImportError:
        return_iframe = True

    if interactive is False:
        # TODO: use carto-python client to create static map?
        pass

    if stylecol:
        fill_style = ('ramp([{stylecol}], '
                      '(#ffc6c4, #ee919b, #cc607d, #9e3963, #672044), '
                      'quantiles)').format(stylecol=stylecol)
    else:
        fill_style = '#f00'

    df_meta = json.loads(self._metadata[-1])
    params = {'username': df_meta['carto_username'],
              'tablename': df_meta['carto_table'],
              'fill_style': fill_style}
    mapconfig = '''{"user_name": "%(username)s",
                    "type": "cartodb",
                    "sublayers": [{
                      "type": "http",
                      "urlTemplate": "http://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png"
                      }, {
                      "sql": "select * from %(tablename)s",
                      "cartocss": "#layer { polygon-fill: %(fill_style)s; polygon-opacity: 0.9; line-color: #FFF; line-opacity: 0.5; }"
                      }],
                      "subdomains": [ "a", "b", "c" ]
                      }''' % params
    params['q'] = urllib.quote(mapconfig)
    # print params
    url = '?'.join(['/files/cartoframes.html',
                    urllib.urlencode(params)])
    iframe = '<iframe src="{url}" width=700 height=350></iframe>'.format(url=url)
    if return_iframe is True:
        return iframe

    return IPython.display.HTML(iframe)

pd.DataFrame.carto_map = carto_map
