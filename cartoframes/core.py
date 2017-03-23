"""
cartoframe methods
~~~~~~~~~~~~~~~~~~

A pandas dataframe interface for working with CARTO maps and tables.

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
import cartoframes.maps as maps
import carto


# NOTE: this is compatible with v1.0.0 of carto-python client
def read_carto(username=None, api_key=None, onprem_url=None, tablename=None,
               query=None, include_geom=True, limit=None, cdb_client=None,
               index='cartodb_id', debug=False):
    """Create a DataFrame from a CARTO table, storing table information in
       pandas metadata that allows for further cartoframe options like syncing,
       map creation, and augmentation from the Data Observatory.

       :param username: CARTO username (default None)
       :type username: string
       :param api_key: CARTO API key
       :type api_key: string
       :param onprem_url: BASEURL for onprem
       :type onprem_url: string
       :param tablename: Table to create a cartoframe from
       :type tablename: string
       :param query: Query for generating a cartoframe
       :type query: string
       :param include_geom: Not implemented
       :type include_geom: boolean
       :param limit: (optional) The maximum number of rows to pull
       :type limit: integer
       :param cdb_client: (optional) CARTO Python SDK authentication client object (default None)
       :type cdb_client: object
       :param index: (optional) Column to use for the index (default `cartodb_id`)
       :type index: string

       :returns: A pandas DataFrame linked to a CARTO table
       :rtype: cartoframe
    """
    import cartoframes.maps as maps
    # TODO: if onprem, use the specified template/domain? instead
    # either cdb_client or user credentials have to be specified
    sql = utils.get_auth_client(username=username,
                                api_key=api_key,
                                baseurl=onprem_url,
                                cdb_client=cdb_client)
    is_org_user = utils.get_is_org_user(sql)

    # construct query
    if tablename is not None and query is None:
        tablequery = 'SELECT * FROM "{tablename}"'.format(tablename=tablename)
        # Add limit if requested
        if limit:
            # TODO: ensure that this does not cause sync problems
            if (limit >= 0) and isinstance(limit, int):
                tablequery += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")
        if debug: print(tablequery)
        _df = utils.df_from_table(tablequery, sql, index=index)
    elif query:
        # NOTE: this registers a carto table if `tablename` is specified
        _df = utils.df_from_query(query, sql, is_org_user, username,
                                  tablename=tablename, debug=debug)
    else:
        raise ValueError("Either `tablename` or `query` (or both) need to be "
                         "specified.")

    # TODO: find out of there's a max length to clip on
    # only make map and set metadata if it's becoming a cartoframe
    if tablename:
        named_map_name = maps.create_named_map(username, api_key,
                                               tablename=tablename)
        print("Named map name: {}".format(named_map_name))

        _df.set_metadata(tablename=tablename,
                         username=username,
                         api_key=api_key,
                         named_map_name=named_map_name,
                         include_geom=include_geom,
                         limit=limit,
                         is_org_user=is_org_user,
                         geomtype=utils.get_geom_type(sql,
                                                      tablename=tablename))

        # save the state for later use
        # NOTE: this doubles the size of the dataframe
        _df.set_last_state()

    # store carto sql client for later use
    _df.set_carto_sql_client(sql)

    return _df


def carto_registered(self):
    """Says whether dataframe is registered as a table on CARTO

    :returns: Whether a DataFrame is registered as a table on CARTO
    :rtype: boolean
    """
    try:
        return self.get_carto_tablename() is not None
    except IndexError:
        return False

def carto_insync(self):
    """Says whether current cartoframe is in sync with last saved state

    :returns: Whether the current state of the cartoframe has changed since last sychronized with CARTO
    :rtype: boolean
    """
    return self.equals(self.carto_last_state)

def set_last_state(self):
    """
    Store the state of the cartoframe

    :returns: None
    """
    self.carto_last_state = self.copy(deep=True)

def set_carto_sql_client(self, sql_client):
    """
    Store the SQL client for later use

    :returns: None
    """
    self.carto_sql_client = sql_client
    # self._metadata[-1] = json.dumps()

def get_carto_sql_client(self):
    """
    Retrieves the internally stored SQL Auth client

    :returns: the internally stored sql client
    :rtype: CARTO SQL Auth client object
    """
    return self.carto_sql_client

# TODO: write a decorator for the following `get` functions
def get_carto_api_key(self):
    """return the username of a cartoframe

    :returns: CARTO API key associated with cartoframe
    :rtype: string
    """
    try:
        return self.get_carto('carto_api_key')
    except KeyError:
        raise Exception("This cartoframe is not registered. "
                        "Use `DataFrame.carto_register()`.")

def get_carto_username(self):
    """return the username of a cartoframe

    :returns: CARTO username associated with cartoframe
    :rtype: string
    """
    try:
        return self.get_carto('carto_username')
    except KeyError:
        raise Exception("This cartoframe is not registered. "
                        "Use `DataFrame.carto_register()`.")

def get_carto_datapage(self):
    """Return the CARTO dataset page

    :returns: URL of data page of dataset on CARTO (behind password if private)
    :rtype: string
    """
    # TODO: generalize this for onprem
    # e.g., https://eschbacher.carto.com/dataset/research_team
    url_template = 'https://{username}.carto.com/dataset/{tablename}'

    return url_template.format(username=self.get_carto_username(),
                               tablename=self.get_carto_tablename())

def get_carto_tablename(self):
    """return the username of a cartoframe

    :returns: Table that cartoframe is associated with
    :rtype: string
    """
    try:
        return self.get_carto('carto_table')
    except KeyError:
        raise Exception("This cartoframe is not registered. "
                        "Use `DataFrame.carto_register()`.")


def get_carto_is_org_user(self):
    """Return whether carto `username` is in a multiuser account or not
    """
    return self.get_carto('carto_is_org_user')


def get_carto_geomtype(self):
    """return the geometry type of the cartoframe

    :returns: Geometry type in table (one of 'point', 'line', 'polygon', or 'None')
    :rtype: text
    """
    return self.get_carto('carto_geomtype')

def get_carto_namedmap(self):
    """Return the named map associated with a cartoframe

    :returns: Name of named map
    :rtype: string
    """
    return self.get_carto('carto_named_map')

def get_carto(self, key):
    """General get method for reading from cartoframe metadata

    :param key: key of item to fetch from metadata. One of `carto_named_map`, `carto_geomtype`, `carto_username`, `carto_table`.
    :type key: string
    :returns: Value stored in cartoframe metadata
    :rtype: any
    """
    import json
    try:
        return json.loads(self._metadata[-1])[key]
    except IndexError:
        raise Exception('DataFrame not linked to CARTO. Use '
                        '`DataFrame.sync_carto()` with a new tablename.')


def set_metadata(self, tablename=None, username=None, api_key=None,
                 include_geom=None, limit=None, is_org_user=None,
                 geomtype=None, named_map_name=None):
    """
    Set method for storing metadata in a dataframe

    :returns: None
    """
    import json
    # NOTE: pylint complains that we're accessing a 'protected member
    #       _metadata of a client class' (appending to _metadata only works
    #       with strings, not JSON, so we're serializing here)
    self._metadata.append(
        json.dumps({'carto_table': tablename,
                    'carto_username': username,
                    'carto_api_key': api_key,
                    'carto_named_map': named_map_name,
                    'carto_include_geom': include_geom,
                    'carto_is_org_user': is_org_user,
                    'carto_limit': limit,
                    'carto_geomtype': geomtype}))
    return None



# TODO: make less buggy about the diff between NaNs and nulls
# NOTE: write
def sync_carto(self, username=None, api_key=None, requested_tablename=None,
               n_batch=20, lnglat_cols=None, debug=False):
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
    :param lnglat_cols: Columns which have the latitude and longitude (in that
        order) for creating the geometry in the database. Once this cartoframe
        syncs, a new column called `the_geom` will be pulled down that is a
        text representation of the geometry.
    :type lnglat_cols: tuple
    """

    if (requested_tablename is not None and username is not None and
            api_key is not None):
        # create table on carto if it doesn't not already exist
        # TODO: make this the main way of intereacting with carto_create
        self.carto_create(username, api_key, requested_tablename, debug=debug,
                          lnglat_cols=lnglat_cols)
        self.set_last_state()
        return None
    elif not self.carto_registered():
        raise Exception("Table not registered with CARTO. Set "
                        "`requested_tablename` flag to a new tablename and " "enter credentials.")

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
def carto_create(self, username, api_key, tablename, lnglat_cols=None,
                 debug=False):
    """Create and populate a table on carto with a dataframe.
    This is a private method, but can be used to create a new table on
    CARTO. It is used in carto_sync if a DataFrame is not yet linked to a
    CARTO table."""

    # give dataframe authentication client
    self.set_carto_sql_client(
        utils.get_auth_client(username=username,
                              api_key=api_key))
    is_org_user = utils.get_is_org_user(self.carto_sql_client)

    final_tablename = self._carto_create_table(tablename, username,
                            is_org_user=is_org_user, debug=debug)
    named_map_name = maps.create_named_map(username, api_key,
                          tablename=final_tablename)
    if debug: print("final_tablename: {}".format(final_tablename))
    self.set_metadata(tablename=final_tablename,
                      username=username,
                      is_org_user=is_org_user,
                      api_key=api_key,
                      named_map_name=named_map_name,
                      include_geom=None,
                      limit=None,
                      geomtype='point' if lnglat_cols else None)
    # TODO: would it be better to cartodbfy after the inserts?
    # TODO: how to ensure some consistency between old index and new one? can cartodb_id be zero-valued?
    self._carto_insert_values(debug=debug)

    # override index
    if 'cartodb_id' in self.columns:
        print("`cartodb_id` will become the new index")
        self.set_index('cartodb_id', inplace=True)
    else:
        self.index = range(1, len(self) + 1)
        self.index.name = 'cartodb_id'

    # add columns
    if lnglat_cols:
        self._update_geom_col(lnglat_cols)
    else:
        # NOTE: carto utility columns are not pulled down. These include:
        #    the_geom, the_geom_webmercator
        pass

    print("New cartoframe created. Table on CARTO is "
          "called `{tablename}`".format(tablename=self.get_carto_tablename()))

    return None


def _update_geom_col(self, lnglat_cols):
    """Private method. Update the_geom with the given lnglat_cols"""
    query = '''
        UPDATE "{tablename}"
        SET the_geom = CDB_LatLng({lat}, {lng})
    '''.format(tablename=self.get_carto_tablename(),
               lng=lnglat_cols[0],
               lat=lnglat_cols[1])
    self.carto_sql_client.send(query)
    # collect the_geom
    resp = self.carto_sql_client.send('''
        SELECT cartodb_id, the_geom
          FROM "{tablename}";
    '''.format(tablename=self.get_carto_tablename()))

    self['the_geom'] = pd.DataFrame(resp['rows'])['the_geom']
    return None


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
    colnames = list(self.columns)
    if debug: print("insert_stem: {}".format(insert_stem))

    for row_num, row in enumerate(self.iterrows()):
        row_vals.append('({rowitems})'.format(
            rowitems=utils.format_row(row[1],
                                      self.dtypes,
                                      colnames)))
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

    :param username: CARTO username
    :type username: string
    :param api_key: CARTO API key
    :type api_key: string
    :param tablename: desired tablename
    :type tablename: string

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
              cartocss=None, basemap=None, figsize=(647, 400),
              center=None, zoom=None, show_position_data=True, debug=False):
    """Produce and return CARTO maps. Can be interactive or static.

    :param interactive: (optional) Value on whether to show an interactive map (True) or static map (False)
    :type interactive: boolean
    :param color: (optional) Styles the map by color (e.g., a choropleth for polygon geometries).

        * If color is a string, can be one of two options:

            - a column name. With this option, CARTO's `TurtoCarto <https://carto.com/blog/styling-with-turbo-carto>`__ is used to create qualitative or category mapping based on the data type.
            - a hex value (beginning with a ``#``) or in the set of `CSS3 named colors <https://www.w3schools.com/colors/colors_names.asp>`__. With this option, all geometries are colored the same.

        * If color is a dict, parse the parameters to custom style the map. Values are:

            - `colname` (required): column name to base the styling on
            - `ramp` (optional): If text, type of color ramp to use. See the `CartoColor repository <https://github.com/CartoDB/CartoColor/blob/master/cartocolor.js>`__ for a full list. If list/tuple, set of hex values.
            - `ramp_provider` (optional): Specify the source of the `ramp` (either `cartocolor` or `colorbrewer`)
            - `num_bins`: Number of divisions for the ramp
            - `quant_method`: Quantification method for dividing the data into classes. Options are `jenks`, `quantiles`, `equal`, or `headtails`. By choosing a custom ramp

    :type color: dict, string
    :param size: (optional) Styles point data by size. Only works with point geometries.

        * If size is an integer, all points are sized by the same value specified.
        * If size is a column name, this option sizes points from a default minimum value of 5 pixels to 25 pixels.
        * If size is a dict, size points by the following values if entered. Defaults will be used if they are not requested.

          - `colname`: column to base the styling off of
          - `max`: maximum marker width (default 25)
          - `min`: minimum marker width (default 5)
          - `quant_method`: type of quantification to use. Options are `jenks`, `quantiles`, `equal`, or `headtails`.

    :type size: integer, string, dict
    :param cartocss: Complete CartoCSS style to apply to your map. This will override `size` and `color` attributes if present.
    :type cartocss: string
    :param options: This can be one of the following:

        * XYZ URL for a custom basemap. See `this list <https://leaflet-extras.github.io/leaflet-providers/preview/>`__ for examples.
        * `CARTO basemap <https://carto.com/location-data-services/basemaps/>`__ styles

          - Specific description: `light_all`, `light_nolabels`, `dark_all`, or `dark_nolabels`
          - General descrption: `light` or `dark`. Specifying one of these results in the best basemap for the map geometries.

        * Dictionary with the following keys:

          - `style`: (required) descrption of the map type (`light` or `dark`)
          - `labels`: (optional) Show labels (`True`) or not (`False`). If this option is not included, the best basemap will be chosen based on what was entered for `style` and the geometry type of the basemap.

    :type options: string or dict
    :param figsize: (optional) Tuple of dimensions (width, height) for output embed or image. Default is (647, 400).
    :type figsize: tuple
    :param center: (optional) A (longitude, latitude) coordinate pair of the center view of a map
    :type center: tuple
    :param show_position_data: Whether to show the center and zoom on an interactive map. This can be useful for finding views for static maps.
    :type show_position_data: boolean
    :returns: an interactive or static CARTO map optionally styled
    :rtype: HTML embed

    """
    import sys
    import cartoframes.styling as styling
    import cartoframes.maps as maps

    if sys.version_info >= (3, 0):
        import urllib.parse as urllib
    else:
        # Python 2
        import urllib
    try:
        import IPython
    except ImportError:
        NotImplementedError("Currently cannot use `carto_map` outside of "
                            "Jupyter notebooks")

    if self.get_carto_geomtype() is None:
        raise ValueError("Cannot make a map because geometries are all null.")

    basemap_url, basemap_style = self.get_basemap(basemap)

    if cartocss is None:
        css = styling.CartoCSS(self, size=size, color=color,
                               cartocss=cartocss, basemap=basemap_style)
        cartocss = css.get_cartocss()

    if debug: print(cartocss)

    # create static map
    # TODO: use carto-python client to create static map (not yet
    #       implemented)
    mapview = {}
    if zoom:
        mapview['zoom'] = zoom
    if center:
        mapview['lon'] = center[0]
        mapview['lat'] = center[1]

    url = self._get_static_snapshot(cartocss, basemap_url, figsize, debug=False)
    img = '<img src="{url}{mapview}" />'.format(
        url=url,
        mapview=urllib.urlencode(mapview))

    if interactive is False:
        return IPython.display.HTML(img)
    else:
        bounds = self.get_bounds()
        bnd_str = ','.join([str(b) for b in [bounds['north'], bounds['east'],
                                             bounds['south'], bounds['west']]])

        mapconfig_params = {'username': self.get_carto_username(),
                            'tablename': self.get_carto_tablename(),
                            'cartocss': cartocss,
                            'basemap': basemap_url,
                            'bounds': bnd_str,
                            'show_position_data': show_position_data}

        mapconfig_params['q'] = urllib.quote(
            maps.get_named_mapconfig(self.get_carto_username(),
                                     self.get_carto_namedmap()))

        baseurl = ('https://rawgit.com/CartoDB/cartoframes/master/'
                   'cartoframes/assets/cartoframes.html')

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
pd.DataFrame.get_basemap = maps.get_basemap
pd.DataFrame.get_carto_is_org_user = get_carto_is_org_user

# internal state methods
pd.DataFrame.carto_registered = carto_registered
pd.DataFrame.carto_insync = carto_insync

# Monkey patch these attributes

pd.DataFrame.carto_sql_client = None
pd.DataFrame.carto_last_state = None
