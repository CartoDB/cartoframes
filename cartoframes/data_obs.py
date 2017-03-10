"""
Data Observatory methods
~~~~~~~~~~~~~~~~~~~~~~~~
"""
import json
import pandas as pd
import cartoframes.utils as utils


# TODO: add desired_colnames=None to signature
def carto_do_augment(self, cols_meta, add_geom_id=False, force_sync=False,
                     debug=False):
    """Augment an existing cartoframe with Data Observatory
        1. check inputs for conflicts
        2. send request to augment carto table: https://gist.github.com/talos/50000ed856eb688c66b10d1054a9bcc6
        3. pull down df with only the added columns (with index)
        4. update self to add new columns

        :param cols_meta: Data observatory measures. Each dict has the following keys:

            * ``numer_id``: measure ID from the Data Observatory catalog https://cartodb.github.io/bigmetadata/index.html
            * ``denominator`` (optional): if value is ``predenominated``, then normalize by an appropriate value
            * ``geom_id`` (optional): geometry level to pull measure information from. TODO: add more to this

        :type cols_meta: list of dicts
        :param add_geom_id: Not currently implemented
        :param force_sync: TODO param
    """
    import json
    if not self.carto_registered():
        raise Exception("This cartoframe is not registered with CARTO. "
                        "Use `DataFrame.carto_register()` first.")
    elif not self.carto_insync() and not force_sync:
        raise Exception("This cartoframe needs to be sync'd with CARTO first. "
                        "Use `DataFrame.carto_sync()` first.")

    new_colnames = self._do_augment(cols_meta, add_geom_id=add_geom_id,
                                   debug=debug)

    if not set(new_colnames).isdisjoint(set(self.columns)):
        # if they share columns, throw an error
        commoncols = list(set(new_colnames) & set(self.columns))
        raise NameError("Columns `{commoncols}` are already "
                        "in the cartoframe".format(commoncols=commoncols))

    # TODO: replace with `pd.read_carto(query='')` or with self.sync() once
    #       the two-way sync is working?
    new_do_table_query = '''
            SELECT cartodb_id, {cols} FROM "{tablename}"
        '''.format(cols=', '.join(['"{}"'.format(col) for col in new_colnames]),
                   tablename=self.get_carto_tablename(),
                   username=self.get_carto_username())
    if debug: print(new_do_table_query)
    resp = self.carto_sql_client.send(new_do_table_query)

    schema = utils.transform_schema(resp['fields'])
    do_df = pd.DataFrame(resp['rows']).set_index('cartodb_id').astype(schema)

    for col in do_df.columns:
        self[col] = do_df[col]

    return None



def read_data_obs(self, hints, debug=False):
    """Read metadata from the data observatory. Experimental Data Observatory
    exploratory tool

    :param hints: measure hints that we're interested in
    :returns: summary of the metadata given ``hints``
    :rtype: pandas.DataFrame
    """

    numerator_query = '''
    SELECT * FROM OBS_GetAvailableNumerators(
        (SELECT ST_SetSRID(ST_Extent(the_geom), 4326)
          FROM {tablename}),
        '{array_of_things}'
    ) numers'''.format(tablename=self.get_carto_tablename(),
                       array_of_things=hints)
    if debug: print(numerator_query)
    return utils.df_from_query(numerator_query,
                               self.carto_sql_client,
                               index=None)

def _do_colname_normalize(entry, debug=False):
    """normalize the new colname"""
    if debug: print(entry)
    return '{numer_colname}{normalization}{numer_timespan}'.format(
        numer_colname=entry['numer_colname'],
        normalization=("{}_".format(entry['normalization']
                                    if entry['normalization'] else '')),
        numer_timespan=entry['numer_timespan'].replace(' - ', '_'))

def _do_augment(self, cols_meta, add_geom_id=None, debug=False):
    """create data observatory columns in a dataset"""
    import json
    username = self.get_carto_username()
    tablename = self.get_carto_tablename()
    # NOTE: `obs_augment_table` needs to be in a user's account
    do_alter = '''
        select obs_augment_table('{username}.{tablename}',
                                 '{cols_meta}');
    '''.format(username=username,
               tablename=tablename,
               cols_meta=json.dumps(cols_meta))
    resp = self.carto_sql_client.send(do_alter)
    if debug: print(resp)

    new_colnames = [_do_colname_normalize(row) for row in resp['rows'][0]['obs_augment_table']]
    if debug: print("New colnames: {}".format(str(new_colnames)))

    return new_colnames

# Monkey patch methods

pd.DataFrame.read_data_obs = read_data_obs
pd.DataFrame.carto_do_augment = carto_do_augment
pd.DataFrame._do_augment = _do_augment
