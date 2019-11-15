# - *- coding: utf- 8 - *-

from __future__ import absolute_import

import hashlib
import logging
import re

import pandas as pd

from ...data import Dataset
from ...utils.geom_utils import geodataframe_from_dataframe
from .service import Service
from ...data.clients import SQLClient

HASH_COLUMN = 'carto_geocode_hash'
BATCH_SIZE = 200
DEFAULT_STATUS = {'gc_status_rel': 'relevance'}


QUOTA_SERVICE = 'hires_geocoder'


def _lock(context, lock_id):
    sql = 'select pg_try_advisory_lock({id})'.format(id=lock_id)
    result = context.execute_query(sql)
    locked = result and result.get('rows', [])[0].get('pg_try_advisory_lock')
    logging.debug('LOCK %s : %s', lock_id, locked)
    return locked


def _unlock(context, lock_id):
    logging.debug('UNLOCK %s', lock_id)
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


def _prefixed_column_or_value(attr, prefix):
    if prefix and attr is not None and attr[0] != "'":
        return "{}.{}".format(prefix, attr)
    return attr


def _hash_expr(street, city, state, country, table_prefix=None):
    street, city, state, country = (_prefixed_column_or_value(v, table_prefix) for v in (street, city, state, country))
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
    return """
      SELECT
        CASE WHEN the_geom IS NULL THEN 'new_nongeocoded' ELSE 'new_geocoded' END AS gc_state,
        COUNT(*) AS count
      FROM {table}
      GROUP BY gc_state
    """.format(
        table=table
    )


def _posterior_summary_query(table):
    return """
    SELECT COUNT(*) AS count
    FROM {table}
    WHERE the_geom IS NULL
    """.format(
        table=table
    )


def _geocode_query(table, street, city, state, country, status):
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

    status_assignment, status_columns = _status_assignment(status)

    query = """
        UPDATE {table}
        SET
            the_geom = _g.the_geom,
            {status_assignment}
            {hash_column} = {hash_expression}
        FROM (SELECT * FROM {geocode_expression}) _g
        WHERE _g.cartodb_id = {table}.cartodb_id
    """.format(
        table=table,
        hash_column=HASH_COLUMN,
        hash_expression=hash_expression,
        geocode_expression=geocode_expression,
        status_assignment=status_assignment
    )

    return (query, status_columns)


STATUS_FIELDS = {
    'relevance': ('numeric', "(_g.metadata->>'relevance')::numeric"),
    'precision': ('text', "_g.metadata->>'precision'"),
    'match_types': ('text', "cdb_dataservices_client.cdb_jsonb_array_casttext(_g.metadata->>'match_types')"),
    '*': ('jsonb', "_g.metadata")
}
STATUS_FIELDS_KEYS = sorted(STATUS_FIELDS.keys())


def _status_column(column_name, field):
    column_type, value = STATUS_FIELDS[field]
    return (column_name, column_type, value)


def _column_assignment(column_name, value):
    return '{} = {},'.format(column_name, value)


def _status_assignment(status):
    status_assignment = ''
    status_columns = []
    if isinstance(status, dict):
        # new style: define status assignments with dictionary
        # {'column_name': 'status_field', ...}
        # allows to assign individual status attributes to columns
        invalid_fields = _list_difference(status.values(), STATUS_FIELDS_KEYS)
        if any(invalid_fields):
            raise ValueError("Invalid status fields {} valid keys are: {}".format(
                invalid_fields,
                STATUS_FIELDS_KEYS))
        columns = [_status_column(name, field) for name, field in list(status.items())]
        status_assignments = [_column_assignment(name, value) for name, _, value in columns]
        status_columns = [(name, type_) for name, type_, _ in columns]
        status_assignment = ''.join(status_assignments)
    elif status:
        # old style: column name
        # stores all status as json in a single column
        name, type_, value = _status_column(status, '*')
        status_columns = [(name, type_)]
        status_assignment = _column_assignment(name, value)
    return (status_assignment, status_columns)


def _hash_as_big_int(text):
    # Calculate a positive bigint hash, hence the 63-bit mask.
    return int(hashlib.sha1(text.encode()).hexdigest(), 16) & ((2**63)-1)


def _set_pre_summary_info(summary, output):
    logging.debug(summary)
    output['total_rows'] = sum(summary.values())
    output['required_quota'] = sum(
        [summary[s] for s in ['new_geocoded', 'new_nongeocoded', 'changed_geocoded', 'changed_nongeocoded']])
    output['previously_geocoded'] = summary.get('previously_geocoded', 0)
    output['previously_failed'] = summary.get('previously_nongeocoded', 0)
    output['records_with_geometry'] = sum(
        summary[s] for s in ['new_geocoded', 'changed_geocoded', 'previously_geocoded'])


def _set_post_summary_info(summary, result, output):
    if result and result.get('total_rows', 0) == 1:
        null_geom_count = result.get('rows')[0].get('count')
        geom_count = output['total_rows'] - null_geom_count
        output['final_records_with_geometry'] = geom_count
        # output['final_records_without_geometry'] = null_geom_count
        output['geocoded_increment'] = output['final_records_with_geometry'] - output['records_with_geometry']
        new_or_changed = sum([summary[s] for s in ['new_geocoded', 'changed_geocoded']])
        output['successfully_geocoded'] = output['geocoded_increment'] + new_or_changed
        output['failed_geocodings'] = output['required_quota'] - output['successfully_geocoded']


def _dup_dataset(dataset):
    # When uploading datasets to temporary tables we don't want to leave the dataset
    # with a `table_name` attribute (of the temporary table, that will be deleted),
    # so we'll use duplicates of the datasets for temporary uploads`
    if dataset.get_query():
        return Dataset(dataset.get_query(), credentials=dataset.credentials)
    elif dataset.table_name:
        return Dataset(dataset.table_name, credentials=dataset.credentials)
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
            raise ValueError("Invalid key for argument {} valid keys are: {}".format(
                invalid_keys_list,
                valid_keys_list)
            )
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


class Geocoding(Service):
    """Geocoding using CARTO data services.
    This requires a CARTO account with and API key that allows for using geocoding services;
    (through explicit argument in constructor or via the default credentials).
    Use of these methods will incur in geocoding credit consumption for the provided account.

    Examples:

        Obtain the number of credits needed to geocode a dataset:

        .. code::

            from data.services import Geocoding
            from cartoframes.auth import set_default_credentials
            set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')
            gc = Geocoding()
            _, info = gc.geocode(dataset, street='address', dry_run=True)
            print(info['required_quota'])

        Geocode a dataframe:

        .. code::

            import pandas
            from data.services import Geocoding
            from cartoframes.data import Dataset
            from cartoframes.auth import set_default_credentials
            set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

            dataframe = pandas.DataFrame([['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address','city'])
            gc = Geocoding()
            geocoded_dataframe, info = gc.geocode(dataframe, street='address', city='city', country={'value': 'Spain'})
            print(geocoded_dataframe)

        Geocode a table:

        .. code::

            import pandas
            from data.services import Geocoding
            from cartoframes.data import Dataset
            from cartoframes.auth import set_default_credentials
            set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

            dataset = Dataset('YOUR_TABLE_NAME')
            gc = Geocoding()
            geocoded_dataset, info = gc.geocode(dataset, street='address', city='city', country={'value': 'Spain'})
            print(geocoded_dataset.download())

        Filter results by relevance:

        .. code::

            import pandas
            from data.services import Geocoding
            from cartoframes.data import Dataset
            from cartoframes.auth import set_default_credentials
            set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

            df = pandas.DataFrame([['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address','city'])
            gc = Geocoding()
            df = gc.geocode(df, street='address', city='city', country={'value': 'Spain'}, status=['relevance']).data
            # show rows with relevance greater than 0.7:
            print(df[df['carto_geocode_relevance']>0.7, axis=1)])

    """

    def __init__(self, credentials=None):
        super(Geocoding, self).__init__(credentials=credentials, quota_service=QUOTA_SERVICE)

    def geocode(self, input_data, street,
                city=None, state=None, country=None,
                status=DEFAULT_STATUS,
                table_name=None, if_exists=Dataset.IF_EXISTS_FAIL,
                dry_run=False, cached=None):
        """Geocode a dataset

        Args:
            input_data (Dataset, DataFrame): a Dataset or DataFrame object to be geocoded.
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
            status (dict, optional): dictionary that defines a mapping from geocoding state
                attributes ('relevance', 'precision', 'match_types') to column names.
                (See https://carto.com/developers/data-services-api/reference/)
                Columns will be added to the result data for the requested attributes.
                By default a column ``gc_status_rel`` will be created for the geocoding
                _relevance_. The special attribute '*' refers to all the status
                attributes as a JSON object.
            table_name (str, optional): the geocoding results will be placed in a new
                CARTO table with this name.
            if_exists (str, optional): Behavior for creating new datasets, only applicable
                if table_name isn't None;
                Options are 'fail', 'replace', or 'append'. Defaults to 'fail'.
            cached (str, optional): name of a table used cache geocoding results. Can only
                be used with DataFrames or queries. This parameter is not compatbile
                with table_name.
            dry_run (bool, optional): no actual geocoding will be performed (useful to
                check the needed quota)

        Returns:
            A named-tuple ``(data, metadata)`` containing  either a ``data`` Dataset or DataFrame
            (same type as the input) and a ``metadata`` dictionary with global information
            about the geocoding process

            The data contains a ``the_geom`` column with point locations for the geocoded addresses
            and also a ``carto_geocode_hash`` that, if preserved, can avoid re-geocoding
            unchanged data in future calls to geocode.
        """

        is_dataframe = False
        if isinstance(input_data, pd.DataFrame):
            is_dataframe = True
            dataset = Dataset(input_data)
        elif isinstance(input_data, Dataset):
            dataset = input_data
        else:
            raise ValueError('Invalid input data type')

        self.columns = dataset.get_column_names()

        if cached:
            if table_name:
                raise ValueError('tablecached geocoding is not compatible with parameters "table_name"')
            return self._cached_geocode(
                input_data, cached, street, city=city, state=state, country=country, dry_run=dry_run)

        city, state, country = [_column_or_value_arg(arg, self.columns) for arg in [city, state, country]]

        if dry_run:
            table_name = None

        input_table_name, is_temporary = self._table_for_geocoding(dataset, table_name, if_exists)

        result_info = self._geocode(input_table_name, street, city, state, country, status, dry_run)

        if dry_run:
            result_dataset = dataset
        else:
            result_dataset = self._fetch_geocoded_table_dataset(input_table_name, is_temporary)

        self._cleanup_geocoded_table(input_table_name, is_temporary)

        result = result_dataset
        if is_dataframe:
            # Note that we return a dataframe whenever the input is dataframe,
            # even if we have uploaded it to a table (table_name is not None).
            if dry_run:
                result = input_data
            else:
                result = result_dataset.dataframe  # if temporary it should have been downloaded
                if result is None:
                    # but if not temporary we need to download it now
                    result = result_dataset.download()
                result = geodataframe_from_dataframe(result)

        return self.result(result, metadata=result_info)

    def _cached_geocode(self, input_data, table_name, street, city=None, state=None, country=None, dry_run=False):
        """
        Geocode a dataframe caching results into a table.
        If the same dataframe if geocoded repeatedly no credits will be spent.
        But note there is a time overhead related to uploading the dataframe to a
        temporary table for checking for changes.
        """
        dataset_cache = Dataset(table_name, credentials=self._credentials)

        if dataset_cache.exists():
            if HASH_COLUMN not in dataset_cache.get_column_names():
                raise ValueError('Cache table {} exists but is not a valid geocode table'.format(table_name))

        if HASH_COLUMN in self.columns or not dataset_cache.exists():
            return self.geocode(
                input_data, street=street, city=city, state=state,
                country=country, table_name=table_name, dry_run=dry_run, if_exists=Dataset.IF_EXISTS_REPLACE)

        tmp_table_name = self._new_temporary_table_name()
        input_dataframe = False
        if isinstance(input_data, pd.DataFrame):
            input_dataframe = True
            input_data = Dataset(input_data)
        else:
            if input_data.is_remote() and input_data.table_name:
                raise ValueError('cached geocoding cannot be used with tables')
        input_data.upload(table_name=tmp_table_name, credentials=self._credentials)

        self._execute_query(
            """
            ALTER TABLE {tmp_table} ADD COLUMN IF NOT EXISTS {hash} text
            """.format(tmp_table=tmp_table_name, hash=HASH_COLUMN))

        hcity, hstate, hcountry = [_column_or_value_arg(arg, self.columns) for arg in [city, state, country]]
        hash_expr = _hash_expr(street, hcity, hstate, hcountry, table_prefix=tmp_table_name)
        self._execute_query(
            """
            UPDATE {tmp_table} SET {hash}={table}.{hash}, the_geom={table}.the_geom
            FROM {table} WHERE {hash_expr}={table}.{hash}
            """.format(tmp_table=tmp_table_name, table=table_name, hash=HASH_COLUMN, hash_expr=hash_expr))

        sql_client = SQLClient(self._credentials)
        sql_client.drop_table(table_name)
        sql_client.rename_table(tmp_table_name, table_name)
        # TODO: should remove the cartodb_id column from the result
        # TODO: refactor to share code with geocode() and call self._geocode() here instead
        # actually to keep hashing knowledge encapsulated (AFW) this should be handled by
        # _geocode using an additional parameter for an input table
        dataset = Dataset(table_name, credentials=self._credentials)
        result, meta = self.geocode(dataset, street=street, city=city, state=state, country=country, dry_run=dry_run)
        if input_dataframe:
            result = geodataframe_from_dataframe(result.download())
        return self.result(result, metadata=meta)

    def _table_for_geocoding(self, dataset, table_name, if_exists):
        temporary_table = False
        input_dataset = dataset
        if input_dataset.is_remote() and input_dataset.table_name:
            # input dataset is a table
            if table_name:
                # Copy input dataset into a new table
                # TODO: select only needed columns
                query = 'SELECT * FROM {table}'.format(table=input_dataset.table_name)
                input_table_name = table_name
                input_dataset = Dataset(query, credentials=self._credentials)
                input_dataset.upload(table_name=input_table_name, credentials=self._credentials, if_exists=if_exists)
            else:
                input_table_name = input_dataset.table_name
        else:
            # input dataset is a query or a dataframe
            if table_name:
                input_table_name = table_name
            else:
                temporary_table = True
                input_table_name = self._new_temporary_table_name()
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

    def _geocode(self, table_name, street, city=None, state=None, country=None, status=None, dry_run=False):
        # Internal Geocoding implementation.
        # Geocode a table's rows not already geocoded in a dataset'

        logging.info('table_name = "%s"', table_name)
        logging.info('street = "%s"', street)
        logging.info('city = "%s"', city)
        logging.info('state = "%s"', state)
        logging.info('country = "%s"', country)
        logging.info('status = "%s"', status)
        logging.info('dry_run = "%s"', dry_run)

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
                    sql, add_columns = _geocode_query(table_name, street, city, state, country, status)

                    add_columns += [(HASH_COLUMN, 'text')]

                    logging.info("Adding columns %s if needed", ', '.join([c[0] for c in add_columns]))
                    alter_sql = "ALTER TABLE {table} {add_columns};".format(
                        table=table_name,
                        add_columns=','.join([
                            'ADD COLUMN IF NOT EXISTS {} {}'.format(name, type) for name, type in add_columns]))
                    self._execute_query(alter_sql)

                    logging.debug("Executing query: %s", sql)
                    result = None
                    try:
                        result = self._execute_long_running_query(sql)
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
                logging.debug("Executing result summary query: %s", sql)
                result = self._context.execute_query(sql)
                _set_post_summary_info(summary, result, output)

        if not aborted:
            # TODO
            # transaction.commit()
            pass

        return output  # TODO: GeocodeResult object

    def _execute_prior_summary(self, dataset_name, street, city, state, country):
        sql = _exists_column_query(dataset_name, HASH_COLUMN)
        logging.debug("Executing check first time query: %s", sql)
        result = self._execute_query(sql)
        if not result or result.get('total_rows', 0) == 0:
            sql = _first_time_summary_query(dataset_name, street, city, state, country)
            logging.debug("Executing first time summary query: %s", sql)
        else:
            sql = _prior_summary_query(dataset_name, street, city, state, country)
            logging.debug("Executing summary query: %s", sql)
        return self._execute_query(sql)
