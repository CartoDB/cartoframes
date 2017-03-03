"""
A pandas dataframe interface for working with CARTO maps and tables

Andy Eschbacher and Stuart Lynn, 2017

Project goals
    * Interact with a CARTO table fully within a Jupyter notebook/pandas
      workflow (read and sync dataframe changes)
    * Like geopandas, have a .carto_map() method which gives back the data
      as a map using carto's maps api and TurboCartoCSS on an optional
      attribute
    * Add CARTO services like the Data Observatory as methods to a dataframe

Features to add: see issues in the repository https://github.com/CartoDB/cartoframes/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement
"""

# TODO: hook into pandas.core?
import pandas as pd
import cartoframes.utils as utils
import carto


# NOTE: this is compatible with v1.0.0 of carto-python client
def read_carto(cdb_client=None, username=None, api_key=None, onprem=False,
               tablename=None, query=None, include_geom=True, sync=True,
               limit=None, index='cartodb_id', debug=False):
    """Import a table from carto into a pandas dataframe, storing
       table information in pandas metadata.
       Inputs:
       :param cdb_client: object CARTO Python SDK authentication client
                          (default None)
       :param username: string CARTO username (default None)
       :param api_key: string CARTO API key
       :param onprem: string BASEURL for onprem (not yet implemented)
       :param tablename: string Table to create a cartoframe from
       :param query: string Query for generating a cartoframe (not yet
                     implemented)
       :param include_geom: string Not yet implemented
       :param sync: boolean Create a cartoframe that can later be sync'd (True)
                    or just pull down data (False)
       :param limit: integer The maximum number of rows to pull
       :param index: string Column to use for the index (default `cartodb_id`)
       """
    import json
    # TODO: if onprem, use the specified template/domain? instead
    # either cdb_client or user credentials have to be specified
    sql = utils.get_auth_client(username=username,
                                api_key=api_key,
                                cdb_client=cdb_client)

    # construct query
    if tablename:
        query = 'SELECT * FROM "{tablename}"'.format(tablename=tablename)
        geomtype = utils.get_geom_type(sql, tablename)
        # Add limit if requested
        if limit:
            # NOTE: what if limit is `all` or `none`?
            # TODO: ensure that this does not cause sync problems
            if (limit >= 0) and isinstance(limit, int):
                query += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")
    elif query:
        # NOTE: not yet implemented
        # TODO: this would have to register a table on CARTO if sync=True
        # query = custom_query
        raise NotImplementedError("Creating a cartoframe from a query is not "
                                  "yet implemented.")
    else:
        raise NameError("Either `tablename` or `query` needs to be specified")

    if debug: print(query)

    # exclude geometry columns if asked
    # TODO: include_geom in cdb_client structure?

    _df = utils.df_from_query(query, sql, index=index)

    # NOTE: pylint complains that we're accessing a 'protected member
    #       _metadata of a client class' (appending to _metadata only works
    #       with strings, not JSON, so we're serializing here)
    _df.set_metadata(tablename=tablename,
                     username=username,
                     api_key=api_key,
                     include_geom=include_geom,
                     limit=limit,
                     geomtype=geomtype)

    # save the state for later use
    # NOTE: this doubles the size of the dataframe
    _df.set_last_state()

    # store carto sql client for later use
    _df.set_carto_sql_client(sql)

    return _df


def carto_registered(self):
    """Says whether dataframe is registered as a table on CARTO"""
    # TODO: write this :)
    return True

def carto_insync(self):
    """Says whether current cartoframe is in sync with last saved state"""
    # TODO: write this :)
    return True

def set_last_state(self):
    """
    Store the state of the cartoframe
    """
    self.carto_last_state = self.copy(deep=True)

def set_carto_sql_client(self, sql_client):
    """
    Store the SQL client for later use
    """
    self.carto_sql_client = sql_client
    # self._metadata[-1] = json.dumps()

def get_carto_sql_client(self):
    """
    return the internally stored sql client
    """
    return self.carto_sql_client

# TODO: write a decorator for the following two functions (more will be added
#       that follow this format)
def get_carto_api_key(self):
    """return the username of a cartoframe"""
    import json
    try:
        return json.loads(self._metadata[-1])['carto_api_key']
    except KeyError:
        raise Exception("This cartoframe is not registered. "
                        "Use `DataFrame.carto_register()`.")

def get_carto_username(self):
    """return the username of a cartoframe"""
    import json
    try:
        return json.loads(self._metadata[-1])['carto_username']
    except KeyError:
        raise Exception("This cartoframe is not registered. "
                        "Use `DataFrame.carto_register()`.")

def get_carto_tablename(self):
    """return the username of a cartoframe"""
    import json
    try:
        return json.loads(self._metadata[-1])['carto_table']
    except KeyError:
        raise Exception("This cartoframe is not registered. "
                        "Use `DataFrame.carto_register()`.")


def get_carto_geomtype(self):
    """return the geometry type of the cartoframe"""
    import json
    return json.loads(self._metadata[-1])['carto_geomtype']


def set_metadata(self, tablename=None, username=None, api_key=None,
                 include_geom=None, limit=None, geomtype=None):
    """
    Method for storing metadata in a dataframe
    """
    import json
    self._metadata.append(
        json.dumps({'carto_table': tablename,
                    'carto_username': username,
                    'carto_api_key': api_key,
                    'carto_include_geom': include_geom,
                    'carto_limit': limit,
                    'carto_geomtype': geomtype}))


# TODO: make less buggy about the diff between NaNs and nulls
def sync_carto(self, createtable=False, username=None, api_key=None,
               requested_tablename=None, n_batch=20, latlng_cols=None,
               is_org_user=False, debug=False):
    """
    :param createtable (boolean): if set, creates a new table with name
                                  `new_tablename` on account connected
                                  through the auth_client
    :param new_tablename (string): new name of table to create from dataframe.
                                   If specified and dataframe was sourced from
                                   CARTO, this will not overwrite the original
                                   table. If specified and dataframe was not
                                   read from CARTO, then this will create a new
                                   table in user's CARTO account.
    """

    if (createtable is True and username is not None and
            api_key is not None):
        # create table on carto if it doesn't not already exist
        # TODO: make this the main way of intereacting with carto_create
        self.carto_create(username, api_key, requested_tablename, debug=debug,
                          is_org_user=is_org_user, latlng_cols=latlng_cols)
        return None
    elif not self.carto_registered():
        raise Exception("Table not registered with CARTO. Set `createtable` "
                        "flag to True")

    if self.equals(self.carto_last_state):
        print("Cartoframe is already synced")
        return None

    # create new column if needed
    # TODO: extract to function
    if len(set(self.columns) - set(self.carto_last_state.columns)) > 0:
        newcols = set(self.columns) - set(self.carto_last_state.columns)
        for col in newcols:
            utils.add_col(self, col, n_batch=n_batch,
                                      debug=debug)

    # drop column if needed
    # TODO: extract to function
    if len(set(self.carto_last_state.columns) - set(self.columns)) > 0:
        discardedcols = set(self.carto_last_state.columns) - set(self.columns)
        for col in discardedcols:
            utils.drop_col(self, col, debug=debug)

    # sync updated values
    # TODO: what happens if rows are removed?
    common_cols = list(set(self.columns) & set(self.carto_last_state.columns))
    if not self[common_cols].equals(self.carto_last_state[common_cols]):
        # NOTE: this updates null-valued cells which have not changed since
        #       np.nan != np.nan is True
        df_diff = (self[common_cols] !=
                   self.carto_last_state[common_cols]).stack()
        df_diff = df_diff[df_diff]
        utils.upsert_table(self, df_diff, debug=debug)

    # update state of dataframe
    self.set_last_state()
    print("Sync completed successfully")

# TODO: add geometry creation (now there is no trigger to fill in `the_geom`
#       like there is for the import api)
def carto_create(self, username, api_key, tablename, latlng_cols=None,
                 is_org_user=False, debug=False):
    """create and populate a table on carto with a dataframe"""

    # give dataframe authentication client
    self.set_carto_sql_client(
        utils.get_auth_client(username=username,
                              api_key=api_key))

    final_tablename = self.carto_create_table(tablename, username,
                            is_org_user=is_org_user, debug=debug)
    if debug: print("final_tablename: {}".format(final_tablename))
    # TODO: fix the geomtype piece, and is_org_user may be important (or some
    #        variation of it) for the onprem-flexible version of this module
    self.set_metadata(tablename=final_tablename,
                      username=username,
                      api_key=api_key,
                      include_geom=None,
                      limit=None,
                      geomtype='point' if latlng_cols else None)
    # TODO: would it be better to cartodbfy after the inserts?
    # TODO: how to ensure some consistency between old index and new one? can cartodb_id be zero-valued?
    self.carto_insert_values(debug=debug)

    # override index
    self.index = range(1, len(self) + 1)
    self.index.name = 'cartodb_id'

    # add columns
    if latlng_cols:
        self._update_geom_col(latlng_cols)
    else:
        # NOTE: carto utility columns are not pulled down. These include:
        #    the_geom, the_geom_webmercator
        pass

    print("New cartoframe created. Table on CARTO is "
          "called `{tablename}`".format(tablename=self.get_carto_tablename()))

    return None


def _update_geom_col(self, latlng_cols):
    """update the_geom with the given latlng_cols"""
    query = '''
        UPDATE "{tablename}"
        SET the_geom = CDB_LatLng({lat}, {lng})
    '''.format(tablename=self.get_carto_tablename(),
               lat=latlng_cols[0],
               lng=latlng_cols[1])
    self.carto_sql_client.send(query)
    # collect the_geom
    resp = self.carto_sql_client.send('''
        SELECT cartodb_id, the_geom
          FROM "{tablename}";
    '''.format(tablename=self.get_carto_tablename()))

    self['the_geom'] = pd.DataFrame(resp['rows'])['the_geom']


def carto_create_table(self, tablename, username,
                       is_org_user=False, debug=False):
    """create table in carto with a specified schema"""
    schema = dict([(col, utils.dtype_to_pgtype(str(dtype), col))
                   for col, dtype in zip(self.columns, self.dtypes)])
    if debug: print(schema)
    query = utils.create_table_query(tablename, schema, username,
                                     is_org_user=is_org_user, debug=debug)
    resp = self.carto_sql_client.send(query)
    if debug: print(resp)

    # return the tablename if successful
    return resp['rows'][0]['cdb_cartodbfytable']

# TODO: how best to handle indexes from a dataframe and the cartodb_id index?
#  1. If a df has more than one index, error out saying that it is unsupported for now
#  2. If index is non-integer, error out saying that it's not compatible
#  3. What happens if it is a named index? if it's the default index, name it cartodb_id, and create the index on carto (carto seems to handle indexes that are in the space of integers, not just natural numbers)
# NOTE: right now it's clumsy on index
def carto_insert_values(self, n_batch=200, debug=False):
    """insert new values into a table"""
    n_items = len(self)
    if debug: print("self has {} rows".format(n_items))
    row_vals = []
    insert_stem = ("INSERT INTO {tablename}({cols}) "
                   "VALUES ").format(tablename=self.get_carto_tablename(),
                                     cols=','.join(self.columns))
    if debug: print("insert_stem: {}".format(insert_stem))

    for row_num, row in enumerate(self.iterrows()):
        row_vals.append('({rowitems})'.format(rowitems=utils.format_row(row[1], self.dtypes)))
        if debug: print("row_num: {0}, row: {1}".format(row_num, row))
        if len(row_vals) == n_batch or row_num == n_items - 1:
            query = ''.join([insert_stem, ', '.join(row_vals), ';'])
            if debug: print("insert query: {}".format(query))
            resp = self.carto_sql_client.send(query)
            if debug: print("insert response: {}".format(resp))
            # reset batch
            row_vals = []
            return None


    return None


def make_cartoframe(self, username, api_key, tablename,
                    api_type=None):
    """
    :param username (string): CARTO username
    :param api_key (string): CARTO API key
    :param tablename (string): desired tablename
    1. instantiate sql client
    2. setup schema on carto
    3.
    """
    if (len(self) > 5000) or (api_type == 'import'):
        # write to csv + use import api
        pass
    elif (len(self) <= 5000) or (api_type == 'sql'):
        sql = utils.get_auth_client(username, api_key)
    else:
        pass

    return None


def carto_map(self, interactive=True, stylecol=None):
    """
        Produce and return CARTO maps or iframe embeds
    """
    try:
        # if Python 3
        import urllib.parse as urllib
    except ImportError:
        # if Python 2
        import urllib
    import IPython

    if (stylecol is not None) and (stylecol not in self.columns):
        raise NameError(('`{stylecol}` not in '
                         'dataframe').format(stylecol=stylecol))
    # create static map
    if interactive is False:
        # TODO: use carto-python client to create static map (not yet
        #       implemented)
        raise NotImplementedError("Static maps are not yet implemented.")

    # TODO: find more robust way to check which metadata item was checked
    mapconfig_params = {'username': self.get_carto_username(),
                        'tablename': self.get_carto_tablename(),
                        'geomtype': self.get_carto_geomtype(),
                        'stylecol': stylecol,
                        'datatype': (str(self[stylecol].dtype)
                                     if stylecol in self.columns
                                     else None)}

    mapconfig_params['q'] = urllib.quote(
        utils.get_mapconfig(mapconfig_params))

    # print(params)
    url = '?'.join(['/files/cartoframes.html',
                    urllib.urlencode(mapconfig_params)])
    iframe = '<iframe src="{url}" width=700 height=350></iframe>'.format(url=url)
    return IPython.display.HTML(iframe)


# Monkey patch these methods to pandas

# higher level functions and methods
pd.read_carto = read_carto
pd.DataFrame.carto_map = carto_map
pd.DataFrame.sync_carto = sync_carto

# carto_create methods
pd.DataFrame.carto_create = carto_create
pd.DataFrame.carto_create_table = carto_create_table
pd.DataFrame.carto_insert_values = carto_insert_values
pd.DataFrame._update_geom_col = _update_geom_col

# set methods
pd.DataFrame.set_last_state = set_last_state
pd.DataFrame.set_carto_sql_client = set_carto_sql_client
pd.DataFrame.set_metadata = set_metadata

# get methods
pd.DataFrame.get_carto_api_key = get_carto_api_key
pd.DataFrame.get_carto_username = get_carto_username
pd.DataFrame.get_carto_tablename = get_carto_tablename
pd.DataFrame.get_carto_geomtype = get_carto_geomtype

# internal state methods
pd.DataFrame.carto_registered = carto_registered
pd.DataFrame.carto_insync = carto_insync

# Monkey patch these attributes

pd.DataFrame.carto_sql_client = None
pd.DataFrame.carto_last_state = None
