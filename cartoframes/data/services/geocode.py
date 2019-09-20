# - *- coding: utf- 8 - *-

from __future__ import absolute_import

import re
import hashlib
import logging
import uuid
import pandas as pd

from ...lib import context
from ...auth import get_default_credentials
from ...data import Dataset

HASH_COLUMN = 'carto_geocode_hash'
BATCH_SIZE = 200


def _lock(context, lock_id):
    sql = 'select pg_try_advisory_lock({id})'.format(id=lock_id)
    result = context.execute_query(sql)
    locked = result and result.get('rows', [])[0].get('pg_try_advisory_lock')
    logging.debug('LOCK %s : %s' % (lock_id, locked))
    return locked


def _unlock(context, lock_id):
    logging.debug('UNLOCK %s' % lock_id)
    sql = 'select pg_advisory_unlock({id})'.format(id=lock_id)
    result = context.execute_query(sql)
    return result and result.get('rows', [])[0].get('pg_advisory_unlock')


class TableGeocodingLock:
    def __init__(self, context, table_name):
        self._context = context
        text_id = 'carto-geocoder-{table_name}'.format(table_name=table_name)
        self.lock_id = _hash_as_big_int(text_id)
        self.locked = False

    def __enter__(self):
        self.locked = _lock(self._context, self.lock_id)
        return self.locked

    def __exit__(self, type, value, traceback):
        if self.locked:
            _unlock(self._context, self.lock_id)


def _column_name(col):
    if col:
        return "$gcparam${col}$gcparam$".format(col=col)
    else:
        return 'NULL'


def _hash_expr(street, city, state, country):
    hashed_expr = " || '<>' || ".join([street, city or "''", state or "''", country or "''"])
    return "md5({hashed_expr})".format(hashed_expr=hashed_expr)


def _needs_geocoding_expr(hash_expr):
    return "({hash_column} IS NULL OR {hash_column} <> {hash_expr})".format(
        hash_column=HASH_COLUMN,
        hash_expr=hash_expr
    )


def _exists_column_query(table, column):
    return """
      SELECT TRUE FROM pg_catalog.pg_attribute a
      WHERE
        a.attname = '{column}'
        AND a.attnum > 0
        AND NOT a.attisdropped
        AND a.attrelid = (
            SELECT c.oid
            FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.oid = '{table}'::regclass::oid
                AND pg_catalog.pg_table_is_visible(c.oid)
        );
    """.format(
        table=table,
        column=column
    )


def _prior_summary_query(table, street, city, state, country):
    hash_expression = _hash_expr(street, city, state, country)
    return """
      SELECT
        CASE WHEN {hash_column} IS NULL THEN
          CASE WHEN the_geom IS NULL THEN 'new_nongeocoded' ELSE 'new_geocoded' END
        WHEN {hash_column} <> {hash_expression} THEN
          CASE WHEN the_geom IS NULL THEN 'changed_nongeocoded' ELSE 'changed_geocoded' END
        ELSE
          CASE WHEN the_geom IS NULL THEN 'previously_nongeocoded' ELSE 'previously_geocoded' END
        END AS gc_state,
        COUNT(*) AS count
      FROM {table}
      GROUP BY gc_state
    """.format(
        table=table,
        hash_expression=hash_expression,
        hash_column=HASH_COLUMN
    )


def _first_time_summary_query(table, street, city, state, country):
    hash_expression = _hash_expr(street, city, state, country)
    return """
      SELECT
        CASE WHEN the_geom IS NULL THEN 'new_nongeocoded' ELSE 'new_geocoded' END AS gc_state,
        COUNT(*) AS count
      FROM {table}
      GROUP BY gc_state
    """.format(
        table=table,
        hash_expression=hash_expression,
        hash_column=HASH_COLUMN
    )


def _posterior_summary_query(table):
    return """
    SELECT COUNT(*) AS count
    FROM {table}
    WHERE the_geom IS NULL
    """.format(
        table=table
    )


def _geocode_query(table, street, city, state, country, metadata):
    hash_expression = _hash_expr(street, city, state, country)
    query = """
        SELECT * FROM {table} WHERE {needs_geocoding}
    """.format(
        table=table,
        needs_geocoding=_needs_geocoding_expr(hash_expression)
    )
    geocode_expression = """
        cdb_dataservices_client.cdb_bulk_geocode_street_point(
            $gcquery${query}$gcquery$,
            {street},
            {city},
            {state},
            {country},
            {batch_size}
        )
    """.format(
        query=query,
        street=_column_name(street),
        city=_column_name(city),
        state=_column_name(state),
        country=_column_name(country),
        batch_size=BATCH_SIZE
    )

    metadata_assignment = ''
    if metadata:
        metadata_assignment = '{col} = _g.metadata,'.format(col=metadata)

    return """
        UPDATE {table}
        SET
            the_geom = _g.the_geom,
            {metadata_assignment}
            {hash_column} = {hash_expression}
        FROM (SELECT * FROM {geocode_expression}) _g
        WHERE _g.cartodb_id = {table}.cartodb_id
    """.format(
        table=table,
        hash_column=HASH_COLUMN,
        hash_expression=hash_expression,
        geocode_expression=geocode_expression,
        metadata_assignment=metadata_assignment
    )


def _hash_as_big_int(text):
    # Calculate a positive bigint hash, hence the 63-bit mask.
    return int(hashlib.sha1(text.encode()).hexdigest(), 16) & ((2**63)-1)


def _generate_temp_table_name(base=None):
    return (base or 'table') + '_' + uuid.uuid4().hex[:10]


def _set_pre_summary_info(summary, output):
    logging.debug(summary)
    output['total_rows'] = sum(summary.values())
    output['required_quota'] = sum([summary[s] for s in ['new_geocoded', 'new_nongeocoded', 'changed_geocoded', 'changed_nongeocoded']])
    output['previously_geocoded'] = summary.get('previously_geocoded', 0)
    output['previously_failed'] = summary.get('previously_nongeocoded', 0)
    output['records_with_geometry'] = sum([summary[s] for s in ['new_geocoded', 'changed_geocoded', 'previously_geocoded']])
    # output['records_without_geometry'] = sum([summary[s] for s in ['new_nongeocoded', 'changed_nongeocoded', 'previously_nongeocoded']])


def _set_post_summary_info(summary, result, output):
    if result and result.get('total_rows', 0) == 1:
        null_geom_count = result.get('rows')[0].get('count')
        geom_count = output['total_rows'] - null_geom_count
        output['final_records_with_geometry'] = geom_count
        # output['final_records_without_geometry'] = null_geom_count
        output['geocoded_increment'] = output['final_records_with_geometry'] - output['records_with_geometry']
        output['successfully_geocoded'] = output['geocoded_increment'] + sum([summary[s] for s in ['new_geocoded', 'changed_geocoded']])
        output['failed_geocodings'] = output['required_quota'] - output['successfully_geocoded']


def _dup_dataset(dataset):
    # When uploading datasets to temporary tables we don't want to leave the dataset
    # with a `table_name` attribute (of the temporary table, that will be deleted),
    # so we'll use duplicates of the datasets for temporary uploads`
    if dataset.get_query():
        return Dataset(dataset.get_query())
    elif dataset.table_name:
        return Dataset(dataset.table_name)
    return Dataset(dataset.dataframe)


GEOCODE_COLUMN_KEY = 'column'
GEOCODE_VALUE_KEY = 'value'
VALID_GEOCODE_KEYS = [GEOCODE_COLUMN_KEY, GEOCODE_VALUE_KEY]


def _list_difference(l1, l2):
    """list substraction compatible with Python2"""
    # return l1 - l2
    return list(set(l1) - set(l2))


def _column_or_value_arg(arg, valid_columns=None):
    if arg is None:
        return None
    is_column = False
    if isinstance(arg, dict):
        invalid_keys = _list_difference(arg.keys(), VALID_GEOCODE_KEYS)
        if any(invalid_keys):
            invalid_keys_list = ', '.join(list(invalid_keys))
            valid_keys_list = ', '.join(VALID_GEOCODE_KEYS)
            raise ValueError("Invalid key for argument {} valid keys are: {}".format(invalid_keys_list, valid_keys_list))
        if len(arg.keys()) != 1:
            valid_keys_list = ', '.join(VALID_GEOCODE_KEYS)
            raise ValueError("Exactly one key of {} must be present in argument".format(valid_keys_list))
        key = list(arg.keys())[0]
        if key == GEOCODE_COLUMN_KEY:
            arg = arg[GEOCODE_COLUMN_KEY]
            is_column = True
        else:
            arg = "'{}'".format(arg[GEOCODE_VALUE_KEY])
    else:
        is_column = True
    if is_column and valid_columns:
        if arg not in valid_columns:
            raise ValueError("Argument is not a valid column name: {}".format(arg))
    return arg


def _remove_column_or_index(dataframe, name):
    # Note: we must support the case that name if both a column and the index
    if name in dataframe.columns:
        del dataframe[name]
    if dataframe.index.name == name:
        dataframe.reset_index(inplace=True)
        del dataframe[name]


class Geocode(object):
    """Geocode using CARTO data services.
    This requires a CARTO account with and API key that allows for using geocoding services;
    (through explicit argument in constructor or via the default credentials).
    Use of these methods will incur in geocoding credit consumption for the provided account.

    Examples:

        Obtain the number of credits needed to geocode a dataset:

        .. code::

            from data.services import Geocode
            from cartoframes.auth import set_default_credentials
            set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')
            gc = Geocode()
            _, info = gc.geocode(dataset, street='address', dry_run=True)
            print(info['required_quota'])

        Geocode a dataframe:

        .. code::

            import pandas
            from data.services import Geocode
            from cartoframes.data import Dataset
            from cartoframes.auth import set_default_credentials
            set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

            dataframe = pandas.DataFrame([['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address','city'])
            gc = Geocode()
            geocoded_dataframe, info = gc.geocode(dataframe, street='address', city='city', country={'value': 'Spain'})
            print(geocoded_dataframe)

        Geocode a table:

        .. code::

            import pandas
            from data.services import Geocode
            from cartoframes.data import Dataset
            from cartoframes.auth import set_default_credentials
            set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

            dataset = Dataset('YOUR_TABLE_NAME')
            gc = Geocode()
            geocoded_dataset, info = gc.geocode(dataset, street='address', city='city', country={'value': 'Spain'})
            print(geocoded_dataset.download())

        Filter results by relevance:

        .. code::

            import pandas
            from data.services import Geocode
            from cartoframes.data import Dataset
            from cartoframes.auth import set_default_credentials
            set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

            df = pandas.DataFrame([['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address','city'])
            gc = Geocode()
            df, info = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, metadata='meta')
            # show rows with relevance greater than 0.7:
            print(df[df.apply(lambda x: json.loads(x['meta'])['relevance']>0.7, axis=1)])

    """

    def __init__(self, credentials=None):
        self._credentials = credentials or get_default_credentials()
        self._context = context.create_context(self._credentials)

    def geocode(self, dataset, street,
                city=None, state=None, country=None,
                metadata=None,
                table_name=None, if_exists=Dataset.FAIL,
                dry_run=False):
        """Geocode a dataset

        Args:
            dataset (Dataset): a Dataset object to be geocoded.
            street (str): name of the column containing postal addresses
            city (dict, optional): dictionary with either a `column` key
                with the name of a column containing the addresses' city names or
                a `value` key with a literal city value value, e.g. 'New York'.
                It also accepts a string, in which case `column` is implied.
            state (dict, optional): dictionary with either a `column` key
                with the name of a column containing the addresses' state names or
                a `value` key with a literal state value value, e.g. 'WA'.
                It also accepts a string, in which case `column` is implied.
            country (dict, optional): dictionary with either a `column` key
                with the name of a column containing the addresses' country names or
                a `value` key with a literal country value value, e.g. 'US'.
                It also accepts a string, in which case `column` is implied.
            metadata (str, optional): name of a column where metadata (in JSON format)
                will be stored (see https://carto.com/developers/data-services-api/reference/)
            table_name (str, optional): the geocoding results will be placed in a new
                CARTO table with this name.
            if_exists (str, optional): Behavior for creating new datasets, only applicable
                if table_name isn't None;
                Options are 'fail', 'replace', or 'append'. Defaults to 'fail'.
            dry_run (bool, optional): no actual geocoding will be performed (useful to
                check the needed quota)

        Returns:
            tuple: (Dataset, info_dict)

        """

        input_dataframe = None
        if isinstance(dataset, pd.DataFrame):
            input_dataframe = dataset
            dataset = Dataset(input_dataframe)

        self.columns = dataset.get_column_names()

        city, state, country = [_column_or_value_arg(arg, self.columns) for arg in [city, state, country]]

        if dry_run:
            table_name = None

        input_table_name, is_temporary = self._table_for_geocoding(dataset, table_name, if_exists)

        result_info = self._geocode(input_table_name, street, city, state, country, metadata, dry_run)

        if dry_run:
            result_dataset = dataset
        else:
            result_dataset = self._fetch_geocoded_table_dataset(input_table_name, is_temporary)

        self._cleanup_geocoded_table(input_table_name, is_temporary)

        if result_dataset.dataframe is not None and not table_name and not dry_run:
            # The result is a permanent table; remove cartodb_id if it wasn't present in the input
            if 'cartodb_id' not in self.columns and 'cartodb_id' in result_dataset.get_column_names():
                _remove_column_or_index(result_dataset.dataframe, 'cartodb_id')

        result = result_dataset
        if input_dataframe is not None:
            # Note that we return a dataframe whenever the input is dataframe,
            # even if we have uploaded it to a table (table_name is not None).
            if dry_run:
                result = input_dataframe
            else:
                result = result_dataset.dataframe  # if temporary it should have been downloaded
                if result is None:
                    # but if not temporary we need to download it now
                    result = result_dataset.download()

        return (result, result_info)

    def _table_for_geocoding(self, dataset, table_name, if_exists):
        temporary_table = False
        input_dataset = dataset
        if input_dataset.is_remote() and input_dataset.table_name:  # FIXME: more robust to check first for query (hasattr(input_dataset, 'query'))
            # input dataset is a table
            if table_name:
                # Copy input dataset into a new table
                # TODO: select only needed columns
                query = 'SELECT * FROM {table}'.format(table=input_dataset.table_name)
                input_table_name = table_name
                input_dataset = Dataset(query)
                input_dataset.upload(table_name=input_table_name, credentials=self._credentials, if_exists=if_exists)
            else:
                input_table_name = input_dataset.table_name
        else:
            # input dataset is a query or a dataframe
            if table_name:
                input_table_name = table_name
            else:
                temporary_table = True
                input_table_name = _generate_temp_table_name()
                input_dataset = _dup_dataset(input_dataset)
            input_dataset.upload(table_name=input_table_name, credentials=self._credentials, if_exists=if_exists)
        return (input_table_name, temporary_table)

    def _fetch_geocoded_table_dataset(self, input_table_name, is_temporary):
        dataset = Dataset(input_table_name, credentials=self._credentials)
        if is_temporary:
            dataset = Dataset(dataset.download())
        return dataset

    def _cleanup_geocoded_table(self, input_table_name, is_temporary):
        if is_temporary:
            Dataset(input_table_name, credentials=self._credentials).delete()

    # Note that this can be optimized for non in-place cases (table_name is not None), e.g.
    # injecting the input query in the geocoding expression,
    # receiving geocoding results instead of storing in a table, etc.
    # But that would make transition to using AFW harder.

    def _geocode(self, table_name, street, city=None, state=None, country=None, metadata=None, dry_run=False):
        # Internal Geocoding implementation.
        # Geocode a table's rows not already geocoded in a dataset'

        logging.info('table_name = "%s"' % table_name)
        logging.info('street = "%s"' % street)
        logging.info('city = "%s"' % city)
        logging.info('state = "%s"' % state)
        logging.info('country = "%s"' % country)
        logging.info('metadata = "%s"' % metadata)
        logging.info('dry_run = "%s"' % dry_run)

        output = {}

        summary = {s: 0 for s in [
            'new_geocoded', 'new_nongeocoded',
            'changed_geocoded', 'changed_nongeocoded',
            'previously_geocoded', 'previously_nongeocoded']}

        # TODO: Use a single transaction so that reported changes (posterior - prior queries)
        # are only caused by the geocoding process. Note that no rollback should be
        # performed once the geocoding update is executed, since
        # quota spent by the Dataservices function would not be rolled back;
        # hence a Python `with` statement is not used here.
        # transaction = connection.begin()

        result = self._execute_prior_summary(table_name, street, city, state, country)
        if result:
            for row in result.get('rows'):
                gc_state = row.get('gc_state')
                count = row.get('count')
                summary[gc_state] = count

        _set_pre_summary_info(summary, output)

        aborted = False

        if output['required_quota'] > 0 and not dry_run:
            with TableGeocodingLock(self._context, table_name) as locked:
                if not locked:
                    output['error'] = 'The table is already being geocoded'
                    output['aborted'] = aborted = True
                else:
                    # Create column to store input search hash
                    add_columns = [(HASH_COLUMN, 'text')]

                    if metadata:
                        # Create column to store result metadata
                        add_columns.append((metadata, 'jsonb'))

                    logging.info("Adding columns {} if needed".format(', '.join([c[0] for c in add_columns])))
                    alter_sql = "ALTER TABLE {table} {add_columns};".format(
                        table=table_name,
                        add_columns=','.join(['ADD COLUMN IF NOT EXISTS {} {}'.format(name, type) for name, type in add_columns]))
                    self._context.execute_query(alter_sql)

                    sql = _geocode_query(table_name, street, city, state, country, metadata)
                    logging.debug("Executing query: %s" % sql)
                    result = None
                    try:
                        result = self._context.execute_long_running_query(sql)
                    except Exception as err:
                        logging.error(err)
                        msg = str(err)
                        output['error'] = msg
                        # FIXME: Python SDK should return proper exceptions
                        # see: https://github.com/CartoDB/cartoframes/issues/751
                        match = re.search(
                            r'Remaining quota:\s+(\d+)\.\s+Estimated cost:\s+(\d+)',
                            msg, re.MULTILINE | re.IGNORECASE
                        )
                        if match:
                            output['remaining_quota'] = int(match.group(1))
                            output['estimated_cost'] = int(match.group(2))
                        aborted = True
                        # Don't rollback to avoid losing any partial geocodification:
                        # TODO
                        # transaction.commit()

                    if result and not aborted:
                        # Number of updated rows not available for batch queries
                        # output['updated_rows'] = result.rowcount
                        # logging.info('Number of rows updated: %d', output['updated_rows'])
                        pass

            if not aborted:
                sql = _posterior_summary_query(table_name)
                logging.debug("Executing result summary query: %s" % sql)
                result = self._context.execute_query(sql)
                _set_post_summary_info(summary, result, output)

        if not aborted:
            # TODO
            # transaction.commit()
            pass

        return output  # TODO: GeocodeResult object

    def _execute_prior_summary(self, dataset_name, street, city, state, country):
        sql = _exists_column_query(dataset_name, HASH_COLUMN)
        logging.debug("Executing check first time query: %s" % sql)
        result = self._context.execute_query(sql)
        if not result or result.get('total_rows', 0) == 0:
            sql = _first_time_summary_query(dataset_name, street, city, state, country)
            logging.debug("Executing first time summary query: %s" % sql)
        else:
            sql = _prior_summary_query(dataset_name, street, city, state, country)
            logging.debug("Executing summary query: %s" % sql)
        return self._context.execute_query(sql)
