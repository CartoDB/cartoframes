"""Data Observatory methods"""
import json
import pandas as pd
import cartoframes.utils

def read_data_obs(self, hints, debug=False):
    """
    Read metadata from the data observatory
    """

    numerator_query = '''
    SELECT * FROM OBS_GetAvailableNumerators(
        (SELECT ST_SetSRID(ST_Extent(the_geom), 4326)
          FROM {tablename}),
        '{array_of_things}'
    ) numers'''.format(tablename=json.loads(self._metadata[-1])['carto_table'],
                       array_of_things=hints)
    if debug: print(numerator_query)
    return utils.df_from_query(numerator_query,
                                           self.carto_sql_client,
                                           index=None)

# TODO: add desired_colnames=None to signature

def carto_do_augment(self, cols_meta, add_geom_id=False, force_sync=False,
                     debug=False):
    """Augment an existing cartoframe with Data Observatory
        1. check inputs for conflicts
        2. send request to augment carto table:
            https://gist.github.com/talos/50000ed856eb688c66b10d1054a9bcc6
        3. pull down df with only the added columns (with index)
        4. update self to add new columns
        :param cols_meta (list of dicts): data observatory measures
    """
    import json
    if not self.carto_registered():
        raise Exception("This cartoframe is not registered with CARTO. "
                        "Use `DataFrame.carto_register()` first.")
    elif not self.carto_insync() and not force_sync:
        raise Exception("This cartoframe needs to be sync'd with CARTO first. "
                        "Use `DataFrame.carto_sync()` first.")

    new_colnames = self.do_augment(cols_meta, add_geom_id=add_geom_id,
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

def _do_colname_normalize(entry, debug=False):
    """normalize the new colname"""
    if debug: print(entry)
    return '{numer_colname}{normalization}{numer_timespan}'.format(
        numer_colname=entry['numer_colname'],
        normalization=("{}_".format(entry['normalization']
                                    if entry['normalization'] else '')),
        numer_timespan=entry['numer_timespan'].replace(' - ', '_'))

def from_carto_do(self,bounding,cols_meta,table_name=None , debug=False):
	metadata_query  = """
  			SELECT cdb_dataservices_client.OBS_GetMeta(
    			{bounding},
				'{cols_meata}',
    		1, 1, 1
  			) meta
		)
	"""

	resp = self.carto_sql_client.send(metadata_query);

	meta = resp['rows'][0]['meta']
	select_vals = ','.join([ "r->{0}->'value' as {1}".foramt(index, col['numer_name']) for index,col in enumerate(json.loads(meta))])
	if debug: print(resp)

	do_generate_table = """
		with geometries as(
			SELECT * FROM OBS_GetBoundariesByGeometry(
      			st_makeenvelope({bounding},4326),
	  			'us.census.tiger.census_tract'
			) As m(the_geom, geoid)

		)
		select {select_vals}, geometries.the_geom  from cdb_dataservices_client.OBS_GetData( (select array_agg(geoid) from geometries) , '{meta}') as r,
		geometries
		where geometries.geoid = r.id
        )
        """.format( meta = meta, select_vals= select_vals)
	if debug: print(do_generate_table)
	resp = self.carto_sql_client.send(do_generate_table)
	return resp


def do_aggregate(self, geom_level, cols_args = None, result_table_name=None):
    username=self.get_carto_username()
    if(result_table_name):
        query = """

        """
    else:
        query = """
        """

def do_augment(self, cols_meta, add_geom_id=None, debug=False):
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

pd.from_carto_do = from_carto_do
pd.DataFrame.read_data_obs = read_data_obs
pd.DataFrame.carto_do_augment = carto_do_augment
pd.DataFrame.do_augment = do_augment
