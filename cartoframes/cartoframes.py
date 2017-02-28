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
import cartoframes_utils
import carto
# TODO: setup carto authentication through a method


# NOTE: this is compatible with v1.0.0 of carto-python client
def read_carto(cdb_client=None, username=None, api_key=None,
               tablename=None, query=None, include_geom=True,
               limit=None, index='cartodb_id', debug=False):
    """Import a table from carto into a pandas dataframe, storing
       table information in pandas metadata.
       Inputs:
       :param cdb_client: object CARTO Python SDK authentication client
                          (default None)
       :param
       """
    from carto.sql import SQLClient
    from carto.auth import APIKeyAuthClient
    import json
    if cdb_client is None:
        BASEURL = 'https://{username}.carto.com/api/'.format(username=USERNAME)
        cdb_client = APIKeyAuthClient(BASEURL, API_KEY)
        sql = SQLClient(cdb_client)
    else:
        sql = SQLClient(cdb_client)

    # construct query
    if tablename:
        query = 'SELECT * FROM "{tablename}"'.format(tablename=tablename)
        geomtype = carto_utils.get_geom_type(sql, tablename)
        # Add limit if requested
        if limit:
            # NOTE: what if limit is `all` or `none`?
            # TODO: ensure that this does not cause sync problems
            if (limit >= 0) and isinstance(limit, int):
                query += ' LIMIT {limit}'.format(limit=limit)
            else:
                raise ValueError("`limit` parameter must an integer >= 0")
    elif query:
        # NOTE: note yet implemented
        # query = custom_query
        raise NotImplementedError("Creating a cartoframe from a query is not "
                                  "yet implemented.")
    else:
        raise NameError("Either `tablename` or `query` needs to be specified")

    if debug:
        print(query)

    # exclude geometry columns if asked
    # TODO: include_geom in cdb_client structure?

    if debug:
        print(query)
    # TODO: how to handle NaNs deterministically?
    resp = sql.send(query)
    schema = carto_utils.transform_schema(resp['fields'])
    carto_utils.df = pd.DataFrame(resp['rows']).set_index(index).astype(schema)

    # TODO: add table schema to the metadata
    # NOTE: pylint complains that we're accessing a 'protected member
    #       carto_utils.metadata of a client class' (appending to _metadata only works
    #       with strings, not JSON, so we're serializing here)
    _df._metadata.append(json.dumps({'carto_table': tablename,
                                     'carto_username': carto_utils.get_username(cdb_client.base_url),
                                     'carto_include_geom': include_geom,
                                     'carto_limit': limit,
                                     'carto_schema': str(schema),
                                     'carto_geomtype': geomtype}))
    _df.carto_last_state = _df.copy(deep=True)
    _df.carto_sql_client = sql
    return _df


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
            carto_utils.add_col(self, col, debug)

    # drop column if needed
    # TODO: extract to function
    if len(set(self.carto_last_state.columns) - set(self.columns)) > 0:
        discardedcols = set(self.carto_last_state.columns) - set(self.columns)
        for col in discardedcols:
            carto_utils.drop_col(self, col, debug)

    # sync updated values
    # TODO: what happens if rows are removed?
    common_cols = list(set(self.columns) & set(self.carto_last_state.columns))
    if not self[common_cols].equals(self.carto_last_state[common_cols]):
        # NOTE: this updates null-valued cells which have not changed since
        #       np.nan != np.nan is True
        df_diff = (self[common_cols] !=
                   self.carto_last_state[common_cols]).stack()
        df_diff = df_diff[df_diff]
        carto_utils.upsert_table(self, df_diff, debug)

    # update state of dataframe
    self.carto_last_state = self.copy(deep=True)
    print("Sync completed successfully")


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
    import json
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
    df_meta = json.loads(self._metadata[-1])
    mapconfig_params = {'username': df_meta['carto_username'],
                        'tablename': df_meta['carto_table'],
                        'geomtype': df_meta['carto_geomtype'],
                        'stylecol': stylecol,
                        'datatype': (str(self[stylecol].dtype)
                                     if stylecol in self.columns
                                     else None)}

    mapconfig_params['q'] = urllib.quote(
        carto_utils.get_mapconfig(mapconfig_params))

    # print(params)
    url = '?'.join(['/files/cartoframes.html',
                    urllib.urlencode(mapconfig_params)])
    iframe = '<iframe src="{url}" width=700 height=350></iframe>'.format(url=url)
    return IPython.display.HTML(iframe)


# Monkey patch these methods to pandas

pd.read_carto = read_carto
pd.DataFrame.carto_map = carto_map
pd.DataFrame.sync_carto = sync_carto
