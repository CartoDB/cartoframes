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

# not currently used
def add_meta(self, **kwargs):
    """
        Set metadata for a dataframe if none has been already set
    """
    for key in kwargs:
        self._metadata[0][key] = kwargs[key]

def map_dtypes(pgtype):
    """
        Map PostgreSQL data types (key) to NumPy/pandas dtypes (value)
    """
    # may not be a complete list, could not find SQL API documentation
    # about data types
    dtypes = {'number': 'float64',
              'date': 'datetime64',
              'string': 'object',
              'geometry': 'object',
              'boolean': 'bool'}
    try:
        return dtypes[pgtype]
    except KeyError:
        return 'object'

def dtype_to_pgtype(dtype, colname):
    """
    Map dataframe types to carto postgres types
    """
    if colname in ('the_geom', 'the_geom_webmercator'):
        return 'geometry'
    else:
        mapping = {'float64': 'numeric',
                   'datetime64': 'date',
                   'object': 'text',
                   'bool': 'boolean'}
        try:
            return mapping[dtype]
        except KeyError:
            return 'string'

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

def get_username(baseurl):
    """
    NOTE: Not compatible with onprem, etc.
    """
    import re
    m = re.search('https://(.*?).carto.com/api/', baseurl)
    return m.group(1)

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
        LIMIT 1'''.format(tablename=tablename))
    try:
        return geomtypes[result['rows'][0]['geomtype']]
    except KeyError:
        print("Warning: cannot map `{tablename}` because it does not have "
              "geometries").format(tablename=tablename)
        return None

# NOTE: this is compatible with v1.0.0 of carto-python client
# TODO: remove username as a param would be nice.. accessible to write to
#       metadata from carto python client?
def read_carto(cdb_client, tablename=None,
               query=None, include_geom=True,
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
                                     'carto_username': get_username(cdb_client.base_url),
                                     'carto_include_geom': include_geom,
                                     'carto_limit': limit,
                                     'carto_schema': str(schema),
                                     'carto_geomtype': geomtype}))
    _df.carto_last_state = _df.copy(deep=True)
    _df.carto_sql_client = sql
    return _df

pd.read_carto = read_carto


# TODO: add into sync_carto function as subfunction?
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
    # TODO: add datetype conversion
    if 'float' in dtype:
        return 'numeric'
    elif 'int' in dtype:
        return 'int'
    elif 'bool' in dtype:
        return 'boolean'
    else:
        return 'text'

def upsert_table(self, df_diff, debug, n_batch=20):
    import json

    n_items = len(df_diff)
    queries = []

    for row_num, row in enumerate(df_diff.iteritems()):
        if debug: print row
        cartodb_id = row[0][0]
        colname = row[0][1]
        upsert_query = '''
        INSERT INTO "{tablename}"("cartodb_id", "{colname}")
             VALUES ({cartodb_id}, {colval})
        ON CONFLICT ("cartodb_id")
        DO UPDATE SET "{colname}" = {colval}
        WHERE EXCLUDED."cartodb_id" = {cartodb_id};
        '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
                   colname=colname,
                   colval=process_item(self.loc[cartodb_id][colname]),
                   cartodb_id=cartodb_id).strip().replace('\n', ' ')
        queries.append(upsert_query)
        # if debug: print upsert_query

        # run batch if at n_batch queries, or at last item
        if (len(queries) == n_batch) or (row_num == n_items - 1):
            batchquery = '\n'.join(queries)
            if debug:
                print "Num characters in batch query: {}".format(len(batchquery))
            resp = self.carto_sql_client.send(batchquery)
            if debug: print resp
            queries = []
    return None


def drop_col(self, colname, debug):
    """
        Drop specified column
    """
    import json
    alter_query = '''
        ALTER TABLE "{tablename}"
        DROP COLUMN "{colname}"
    '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
               colname=colname)

    if debug: print alter_query
    resp = self.carto_sql_client.send(alter_query)
    if debug: print resp
    return None


def add_col(self, colname, debug):
    """
        Alter table add col
    """
    import json
    if debug: print "Create new column {col}".format(col=colname)
    alter_query = '''
        ALTER TABLE "{tablename}"
        ADD COLUMN "{colname}" {datatype}
    '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
               colname=colname,
               datatype=datatype_map(str(self.dtypes[colname])))
    if debug: print alter_query
    # add column
    resp = self.carto_sql_client.send(alter_query)
    if debug: print resp
    # update all the values in that column
    # NOTE: fails if colval is 'inf' or some other Python or NumPy type
    for item in self[colname].iteritems():
        if debug: print item
        update_query = '''
            UPDATE "{tablename}"
            SET "{colname}" = {colval}
            WHERE "cartodb_id" = {cartodb_id};
        '''.format(tablename=json.loads(self._metadata[0])['carto_table'],
                   colname=colname,
                   colval=process_item(item[1]),
                   cartodb_id=item[0])
        if debug: print update_query
        resp = self.carto_sql_client.send(update_query)
        # if debug: print resp.text
    return None

def create_carto_table(self, auth_client, tablename, debug=False):
    """

    """
    schema = dict([(col, dtype_to_pgtype(str(dtype), colname))
                   for col, dtype in zip(self.columns, self.dtypes)])
    return None

# TODO: make less buggy about the diff between NaNs and nulls
def sync_carto(self, createtable=False, auth_client=None,
               new_tablename=None, debug=False):
    """
        :param createtable (boolean): if set, creates a new table with name
                                      `new_tablename` on account connected
                                      through the auth_client
        :param auth_client (object): carto api auth client
        :param new_tablename (string): new name of table to create from
                                       dataframe
    """

    import json

    # create table on carto if it doesn't not already exist
    if createtable is True:
        # TODO: build this
        # grab df schema, setup table, cartodbfy, then exit
        if auth_client is None:
            raise Exception("Set `auth_client` flag to create a table.")
        raise NotImplementedError("This feature is not yet implemented.")
    elif not hasattr(self, 'carto_sql_client'):
        raise Exception("Table not registered with CARTO. Set `createtable` "
                        "flag to True")

    # create new column if needed
    # TODO: extract to function
    if len(set(self.columns) - set(self.carto_last_state.columns)) > 0:
        newcols = set(self.columns) - set(self.carto_last_state.columns)
        for col in newcols:
            add_col(self, col, debug)

    # drop column if needed
    # TODO: extract to function
    if len(set(self.carto_last_state.columns) - set(self.columns)) > 0:
        discardedcols = set(self.carto_last_state.columns) - set(self.columns)
        for col in discardedcols:
            drop_col(self, col, debug)

    # sync updated values
    # TODO: what happens if rows are removed?
    common_cols = list(set(self.columns) & set(self.carto_last_state.columns))
    if not self[common_cols].equals(self.carto_last_state[common_cols]):
        # NOTE: this updates null-valued cells which have not changed since
        #       np.nan != np.nan is True
        df_diff = (self[common_cols] !=
                   self.carto_last_state[common_cols]).stack()
        df_diff = df_diff[df_diff]
        upsert_table(self, df_diff, debug)

    # update state of dataframe
    self.carto_last_state = self.copy(deep=True)
    print "Sync completed successfully"

pd.DataFrame.sync_carto = sync_carto

def cartocss_by_geom(geomtype):
    if geomtype == 'point':
        markercss = '''
            #layer {
              marker-width: 7;
              marker-fill: %(filltype)s;
              marker-fill-opacity: 1;
              marker-allow-overlap: true;
              marker-line-width: 1;
              marker-line-color: #FFF;
              marker-line-opacity: 1;
            }
        '''.replace('\n', '')
        return markercss
    elif geomtype == 'line':
        linecss = '''
            #layer {
              line-width: 1.5;
              line-color: %(filltype)s;
            }
        '''.replace('\n', '')
        return linecss
    elif geomtype == 'polygon':
        polygoncss = '''
            #layer {
              polygon-fill: %(filltype)s;
              line-width: 0.5;
              line-color: #FFF;
              line-opacity: 0.5;
            }
        '''.replace('\n', '')
        return polygoncss
    return None


def get_fillstyle(params):
    """

    """
    if 'colorramp' not in params:
        pass
    if params['stylecol']:
        if params['datatype'] == 'float64':
            fillstyle = ('ramp([{stylecol}], cartocolor(RedOr), '
                         'quantiles())'.format(stylecol=params['stylecol']))
        else:
            fillstyle = ('ramp([{stylecol}], cartocolor(Bold), '
                         'category(10))'.format(stylecol=params['stylecol']))
    else:
        fillstyle = '#f00'

    return fillstyle


def get_mapconfig(params):
    """
        Anonymous Maps API template for carto.js
        mapconfig_params = {'username': df_meta['carto_username'],
                            'tablename': df_meta['carto_table'],
                            'geomtype': df_meta['geomtype'],
                            'stylecol': stylecol,
                            'datatype': str(self[stylecol].dtype)}
        dtypes one of
          * quantitative: float64 (float32, int32, int64)
          * categorical: bool, object
            * cartocss rule: ramp([room_type], cartocolor(Bold), category(4))
              dtypes = {'number': 'float64',
                        'date': 'datetime64',
                        'string': 'object',
                        'geometry': 'object',
                        'boolean': 'bool'}
        color palettes: https://github.com/CartoDB/CartoColor/blob/master/cartocolor.js
    """

    cartocss = cartocss_by_geom(params['geomtype']) % {'filltype': get_fillstyle(params)}

    hyperparams = dict({'cartocss': cartocss}, **params)
    # print hyperparams

    mapconfig = '''{"user_name": "%(username)s",
                    "type": "cartodb",
                    "sublayers": [{
                      "type": "http",
                      "urlTemplate": "http://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png"
                      }, {
                      "sql": "select * from %(tablename)s",
                      "cartocss": "%(cartocss)s"
                      }],
                      "subdomains": [ "a", "b", "c" ]
                      }''' % hyperparams

    return mapconfig

def carto_map(self, interactive=True, stylecol=None):
    """
        Produce and return CARTO maps or iframe embeds
    """
    import urllib
    import json
    import IPython

    if (stylecol is not None) and (stylecol not in self.columns):
        raise NameError(('`{stylecol}` not in '
                         'dataframe').format(stylecol=stylecol))
    # create static map
    if interactive is False:
        # TODO: use carto-python client to create static map (not yet
        #       implemented)
        raise NotImplementedError("This feature is not yet implemented")

    df_meta = json.loads(self._metadata[-1])
    mapconfig_params = {'username': df_meta['carto_username'],
                        'tablename': df_meta['carto_table'],
                        'geomtype': df_meta['carto_geomtype'],
                        'stylecol': stylecol,
                        'datatype': (str(self[stylecol].dtype)
                                     if stylecol in self.columns
                                     else None)}

    mapconfig_params['q'] = urllib.quote(get_mapconfig(mapconfig_params))

    # print params
    url = '?'.join(['/files/cartoframes.html',
                    urllib.urlencode(mapconfig_params)])
    iframe = '<iframe src="{url}" width=700 height=350></iframe>'.format(url=url)
    return IPython.display.HTML(iframe)

pd.DataFrame.carto_map = carto_map
