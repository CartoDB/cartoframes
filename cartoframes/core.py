"""
cartoframe methods
~~~~~~~~~~~~~~~~~~

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
def read_carto(username=None, api_key=None, onprem=False, tablename=None,
               query=None, include_geom=True, is_org_user=False, limit=None,
               cdb_client=None, index='cartodb_id', debug=False):
    """Create a DataFrame from a CARTO table, storing table information in
       pandas metadata that allows for further cartoframe options like syncing,
       map creation, and augmentation from the Data Observatory.

       :param username: CARTO username (default None)
       :type username: string
       :param api_key: CARTO API key
       :type api_key: string
       :param onprem: BASEURL for onprem (not yet implemented)
       :type onprem: string
       :param tablename: Table to create a cartoframe from
       :type tablename: string
       :param query: Query for generating a cartoframe
       :type query: string
       :param include_geom: Not implemented
       :type include_geom: boolean
       :param sync: Create a cartoframe that can later be sync'd (defaut: True) or just pull down data (False)
       :type sync: boolean
       :param limit: The maximum number of rows to pull
       :type limit: integer
       :param cdb_client: (optional) CARTO Python SDK authentication client object (default None)
       :type param: object
       :param index: (optional) string Column to use for the index (default `cartodb_id`)
       :type index: string

       :returns: A pandas DataFrame linked to a CARTO table
       :rtype: cartoframe
       """
    import json
    import time
    import cartoframes.maps as maps
    # TODO: if onprem, use the specified template/domain? instead
    # either cdb_client or user credentials have to be specified
    sql = utils.get_auth_client(username=username,
                                api_key=api_key,
                                cdb_client=cdb_client)

    # construct query
    if tablename is not None and query is None:
        query = 'SELECT * FROM "{tablename}"'.format(tablename=tablename)
        # Add limit if requested
        if limit:
            # NOTE: what if limit is `all` or `none`?
            # TODO: ensure that this does not cause sync problems
            if (limit >= 0) and isinstance(limit, int):
                query += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")
        if debug: print(query)
        _df = utils.df_from_table(query, sql, index=index)
    elif query:
        # NOTE: not yet implemented
        # TODO: this would have to register a table on CARTO if sync=True
        _df = utils.df_from_query(query, sql, is_org_user, username,
                                  tablename=tablename, debug=debug)
    else:
        raise NameError("Either `tablename` or `query` (or both) needs to be "
                        "specified")

    # NOTE: pylint complains that we're accessing a 'protected member
    #       _metadata of a client class' (appending to _metadata only works
    #       with strings, not JSON, so we're serializing here)

    # TODO: find out of there's a max length to clip on
    named_map_name = maps.create_named_map(username, api_key, tablename)
    print("Named map name: {}".format(named_map_name))

    # only set metadata if it's becoming a cartoframe
    if tablename:
        _df.set_metadata(tablename=tablename,
                         username=username,
                         api_key=api_key,
                         named_map_name=named_map_name,
                         include_geom=include_geom,
                         limit=limit,
                         geomtype=utils.get_geom_type(sql, tablename))

        # save the state for later use
        # NOTE: this doubles the size of the dataframe
        _df.set_last_state()

        # store carto sql client for later use
        _df.set_carto_sql_client(sql)

    return _df


def carto_registered(self):
    """Says whether dataframe is registered as a table on CARTO"""
    try:
        return self.get_carto_tablename() is not None
    except IndexError:
        return False

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

def get_carto_namedmap(self):
    return self.get_carto('carto_named_map')

def get_carto(self, key):
    import json
    return json.loads(self._metadata[-1])[key]


def set_metadata(self, tablename=None, username=None, api_key=None,
                 include_geom=None, limit=None, geomtype=None,
                 named_map_name=None):
    """
    Method for storing metadata in a dataframe
    """
    import json
    self._metadata.append(
        json.dumps({'carto_table': tablename,
                    'carto_username': username,
                    'carto_api_key': api_key,
                    'carto_named_map': named_map_name,
                    'carto_include_geom': include_geom,
                    'carto_limit': limit,
                    'carto_geomtype': geomtype}))


# TODO: make less buggy about the diff between NaNs and nulls
def sync_carto(self, username=None, api_key=None, requested_tablename=None,
               n_batch=20, latlng_cols=None, is_org_user=False, debug=False):
    """If an existing cartoframe, this method syncs with the CARTO table a
        cartoframe is associated with. If syncing a DataFrame which has not yet
        been linked with CARTO, it creates a new table if the tablename does
        not yet exist and updates the metadata in the DataFrame.

    :param username: CARTO username credentials. Needed only if the DataFrame
        is not yet linked to CARTO (e.g., it was created with
        ``pd.DataFrame.read_carto``)
    :type username: string
    :param api_key: CARTO API key. Needed only if linking a DataFrame with a
        table on CARTO.
    :type api_key: string
    :param requested_tablename: if set, creates a new table with name
        `new_tablename` on account connected through the auth_client. If this
        tablename exists on CARTO already, an exception will be thrown.
    :type requested_tablename: string
    :param n_batch: Number of queries to include in a batch update to the
        database (experimental).
    :type n_batch: integer
    :param latlng_cols: Columns which have the latitude and longitude (in that
        order) for creating the geometry in the database. Once this cartoframe
        syncs, a new column called `the_geom` will be pulled down that is a
        text representation of the geometry.
    :type latlng_cols: tuple
    :param is_org_user: This flag needs to be set if a user is in a
        multiuser account.
    :type is_org_user: boolean
    """

    if (requested_tablename is not None and username is not None and
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
    """Create and populate a table on carto with a dataframe.
    This is a private method, but can be used to create a new table on
    CARTO. It is used in carto_sync if a DataFrame is not yet linked to a
    CARTO table."""

    # give dataframe authentication client
    self.set_carto_sql_client(
        utils.get_auth_client(username=username,
                              api_key=api_key))

    final_tablename = self._carto_create_table(tablename, username,
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
    self._carto_insert_values(debug=debug)

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
    """Private method. Update the_geom with the given latlng_cols"""
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


def _carto_create_table(self, tablename, username,
                       is_org_user=False, debug=False):
    """Private method. Create table in carto with a specified schema"""
    schema = dict([(col, utils.dtype_to_pgtype(str(dtype), col))
                   for col, dtype in zip(self.columns, self.dtypes)])
    if debug: print(schema)
    query = utils.create_table_query(tablename, schema, username,
                                     is_org_user=is_org_user, debug=debug)
    resp = self.carto_sql_client.send(query)
    if debug: print(resp)

    # return the tablename if successful
    return resp['rows'][0]['cdb_cartodbfytable']

# TODO: create a batch class which retains information about the batch size and
#       the request being built up
# TODO: how best to handle indexes from a dataframe and the cartodb_id index?
#  1. If a df has more than one index, error out saying that it is unsupported for now
#  2. If index is non-integer, error out saying that it's not compatible
#  3. What happens if it is a named index? if it's the default index, name it cartodb_id, and create the index on carto (carto seems to handle indexes that are in the space of integers, not just natural numbers)
# NOTE: right now it's clumsy on index
def _carto_insert_values(self, n_batch=10000, debug=False):
    """Private method. Insert new values into a table"""
    n_items = len(self)
    if debug: print("self has {} rows".format(n_items))
    row_vals = []
    char_count = 0
    insert_stem = ("INSERT INTO {tablename}({cols}) "
                   "VALUES ").format(tablename=self.get_carto_tablename(),
                                     cols=','.join(self.columns))
    if debug: print("insert_stem: {}".format(insert_stem))

    for row_num, row in enumerate(self.iterrows()):
        row_vals.append('({rowitems})'.format(rowitems=utils.format_row(row[1], self.dtypes)))
        char_count += len(row_vals[-1])
        if debug: print("row_num: {0}, row: {1}".format(row_num, row))
        # run query if at batch size, end of dataframe, or near POST limit
        if (len(row_vals) == n_batch or
                row_num == n_items - 1 or char_count > 900000):

            query = ''.join([insert_stem, ', '.join(row_vals), ';'])
            if debug: print("insert query: {}".format(query))
            resp = self.carto_sql_client.send(query)
            if debug: print("insert response: {}".format(resp))

            # reset batch
            row_vals = []
            char_count = 0


    return None


def make_cartoframe(self, username, api_key, tablename,
                    api_type=None):
    """Placeholder method (not functioning)

    1. instantiate sql client
    2. setup schema on carto
    3. ...

    :param username (string): CARTO username
    :param api_key (string): CARTO API key
    :param tablename (string): desired tablename

    """
    if (len(self) > 5000) or (api_type == 'import'):
        # write to csv + use import api
        pass
    elif (len(self) <= 5000) or (api_type == 'sql'):
        # sql = utils.get_auth_client(username, api_key)
        pass
    else:
        pass

    return None


def carto_map(self, interactive=True, color=None, size=None,
              cartocss=None, basemap=None, figsize=(647, 400), debug=False):
    """Produce and return CARTO maps. Can be interactive or static.

    :param interactive: (optional) Value on whether to show an interactive map or static map
    :type interactive: boolean
    :param color: (optional)

        * If color is a string, can be a column name or a hex value (beginning with a ``#``). When a hex value, all geometries are colored the same. If the column name, use CARTO's TurtoCarto to create qualitative or category mapping.
        * If color is a dict, parse the parameters to custom style the map. Values are:

            - colname (required): column name to base the styling on
            - ramp (optional): If text, type of color ramp to use. See https://github.com/CartoDB/CartoColor/blob/master/cartocolor.js for a full list. If list/tuple, set of hex values.
            - ramp_provider (optional): Specify the source of the `ramp` (either `cartocolor` or `colorbrewer`)
            - num_bins: Number of divisions for the ramp
            - quant_method: Quantification method for dividing the data into classes. Options are `jenks`, `quantiles`, `equal`, or `headtails`. By choosing a custom ramp

    :type color: dict, string
    :param size: (optional) Only works with point geometries. A future version will allow more sizing options for lines.

        * If size is an integer, all points are sized by the same value specified.
        * If size is a column name, this option sizes points from a default minimum value of 4 pixels to 15 pixels.
        * If size is a dict, size points by the following values if entered. Defaults will be used if they are not requested.

          - colname: column to base the styling off of
          - max: maximum marker width (default 15)
          - min: minimum marker width (default 4)
          - quant_method: type of quantification to use. Options are `jenks`, `quantiles`, `equal`, or `headtails`.

    :type size: integer, string, dict
    :param cartocss: Complete CartoCSS style to apply to your map. This will override `size` and `color` attributes if present.
    :type cartocss: string
    :param basemap: (optional) XYZ URL template for the basemap. See https://leaflet-extras.github.io/leaflet-providers/preview/ for examples.
    :type basemap: string
    :param figsize: (optional) Tuple of dimensions (width, height) for output embed or image. Default is (647, 400).
    :type figsize: tuple
    :returns: an interactive or static CARTO map optionally styled
    :rtype: HTML embed

    """
    import cartoframes.styling as styling
    import cartoframes.maps as maps
    try:
        # if Python 3
        import urllib.parse as urllib
    except ImportError:
        # if Python 2
        import urllib
    import IPython

    if cartocss is None:
        css = styling.CartoCSS(self, size=size,
                               color=color, cartocss=cartocss)
        cartocss = css.get_cartocss()

    if debug: print(cartocss)

    # create static map
    # TODO: use carto-python client to create static map (not yet
    #       implemented)
    url = self._get_static_snapshot(cartocss, basemap, figsize, debug=False)
    img = '<img src="{url}" />'.format(url=url)

    if interactive is False:
        return IPython.display.HTML(img)
    else:
        bounds = self.get_bounds()
        mapconfig_params = {'username': self.get_carto_username(),
                            'tablename': self.get_carto_tablename(),
                            'cartocss': cartocss,
                            'basemap': basemap,
                            'bounds': ','.join(map(str, [bounds['north'], bounds['east'],
                                       bounds['south'], bounds['west']]))}

        mapconfig_params['q'] = urllib.quote(
            maps.get_named_mapconfig(self.get_carto_username(),
                                     self.get_carto_namedmap()))

        baseurl = 'https://cdn.rawgit.com/andy-esch/6d993d3f25c5856ea38d1f374e57722e/raw/ce30379f35aafd027816f065b4e5c52f881c4a86/index.html'

        url = '?'.join([baseurl,
                        urllib.urlencode(mapconfig_params)])

        if debug: print(url)
        iframe = ('<iframe src="{url}" width={width} height={height}>'
                  'Preview image: {img}</iframe>').format(url=url,
                                                          width=figsize[0],
                                                          height=figsize[1],
                                                          img=img)
        return IPython.display.HTML(iframe)


# Monkey patch these methods to pandas

# higher level functions and methods
pd.read_carto = read_carto
pd.DataFrame.carto_map = carto_map
pd.DataFrame.sync_carto = sync_carto

# carto_create methods
pd.DataFrame.carto_create = carto_create
pd.DataFrame._carto_create_table = _carto_create_table
pd.DataFrame._carto_insert_values = _carto_insert_values
pd.DataFrame._update_geom_col = _update_geom_col

# set methods
pd.DataFrame.set_last_state = set_last_state
pd.DataFrame.set_carto_sql_client = set_carto_sql_client
pd.DataFrame.set_metadata = set_metadata

# get methods
pd.DataFrame.get_carto = get_carto
pd.DataFrame.get_carto_api_key = get_carto_api_key
pd.DataFrame.get_carto_username = get_carto_username
pd.DataFrame.get_carto_tablename = get_carto_tablename
pd.DataFrame.get_carto_geomtype = get_carto_geomtype
pd.DataFrame.get_carto_namedmap = get_carto_namedmap

# internal state methods
pd.DataFrame.carto_registered = carto_registered
pd.DataFrame.carto_insync = carto_insync

# Monkey patch these attributes

pd.DataFrame.carto_sql_client = None
pd.DataFrame.carto_last_state = None
