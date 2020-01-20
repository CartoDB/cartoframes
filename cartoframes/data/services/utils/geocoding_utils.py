
import logging
import hashlib
from . import geocoding_constants

__all__ = [
    'lock',
    'unlock',
    'prefixed_column_or_value',
    'hash_expr',
    'needs_geocoding_expr',
    'exists_column_query',
    'prior_summary_query',
    'first_time_summary_query',
    'posterior_summary_query',
    'geocode_query',
    'status_column',
    'column_assignment',
    'status_assignment_columns',
    'hash_as_big_int',
    'set_pre_summary_info',
    'set_post_summary_info',
    'list_difference',
    'column_or_value_arg'
]


def lock(execute_query, lock_id):
    sql = 'select pg_try_advisory_lock({id})'.format(id=lock_id)
    result = execute_query(sql)
    locked = result and result.get('rows', [])[0].get('pg_try_advisory_lock')
    logging.debug('LOCK %s : %s', lock_id, locked)
    return locked


def unlock(execute_query, lock_id):
    logging.debug('UNLOCK %s', lock_id)
    sql = 'select pg_advisory_unlock({id})'.format(id=lock_id)
    result = execute_query(sql)
    return result and result.get('rows', [])[0].get('pg_advisory_unlock')


def column_name(col):
    if col:
        return "$gcparam${col}$gcparam$".format(col=col)
    else:
        return 'NULL'


def prefixed_column_or_value(attr, prefix):
    if prefix and attr is not None and attr[0] != "'":
        return "{}.{}".format(prefix, attr)
    return attr


def hash_expr(street, city, state, country, table_prefix=None):
    street, city, state, country = (prefixed_column_or_value(v, table_prefix) for v in (street, city, state, country))
    hashed_expr = " || '<>' || ".join([street, city or "''", state or "''", country or "''"])
    return "md5({hashed_expr})".format(hashed_expr=hashed_expr)


def needs_geocoding_expr(hash_expr):
    return "({hash_column} IS NULL OR {hash_column} <> {hash_expr})".format(
        hash_column=geocoding_constants.HASH_COLUMN,
        hash_expr=hash_expr
    )


def exists_column_query(table, column):
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


def prior_summary_query(table, street, city, state, country):
    hash_expression = hash_expr(street, city, state, country)
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
        hash_column=geocoding_constants.HASH_COLUMN
    )


def first_time_summary_query(table, street, city, state, country):
    return """
      SELECT
        CASE WHEN the_geom IS NULL THEN 'new_nongeocoded' ELSE 'new_geocoded' END AS gc_state,
        COUNT(*) AS count
      FROM {table}
      GROUP BY gc_state
    """.format(
        table=table
    )


def posterior_summary_query(table):
    return """
    SELECT COUNT(*) AS count
    FROM {table}
    WHERE the_geom IS NULL
    """.format(
        table=table
    )


def geocode_query(table, schema, street, city, state, country, status):
    hash_expression = hash_expr(street, city, state, country)
    query = """
        SELECT * FROM "{schema}"."{table}" WHERE {needs_geocoding}
    """.format(
        table=table,
        schema=schema,
        needs_geocoding=needs_geocoding_expr(hash_expression)
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
        street=column_name(street),
        city=column_name(city),
        state=column_name(state),
        country=column_name(country),
        batch_size=geocoding_constants.BATCH_SIZE
    )

    status_assignment, status_columns = status_assignment_columns(status)

    query = """
        UPDATE "{schema}"."{table}"
        SET
            the_geom = _g.the_geom,
            {status_assignment}
            {hash_column} = {hash_expression}
        FROM (SELECT * FROM {geocode_expression}) _g
        WHERE _g.cartodb_id = "{schema}"."{table}".cartodb_id
    """.format(
        table=table,
        schema=schema,
        hash_column=geocoding_constants.HASH_COLUMN,
        hash_expression=hash_expression,
        geocode_expression=geocode_expression,
        status_assignment=status_assignment
    )

    return (query, status_columns)


def status_column(column_name, field):
    column_type, value = geocoding_constants.STATUS_FIELDS[field]
    return (column_name, column_type, value)


def column_assignment(column_name, value):
    return '{} = {},'.format(column_name, value)


def status_assignment_columns(status):
    status_assignment = ''
    status_columns = []
    if isinstance(status, dict):
        # new style: define status assignments with dictionary
        # {'column_name': 'status_field', ...}
        # allows to assign individual status attributes to columns
        invalid_fields = list_difference(status.values(), geocoding_constants.STATUS_FIELDS_KEYS)
        if any(invalid_fields):
            raise ValueError("Invalid status fields {} valid keys are: {}".format(
                invalid_fields,
                geocoding_constants.STATUS_FIELDS_KEYS))
        columns = [status_column(name, field) for name, field in list(status.items())]
        status_assignments = [column_assignment(name, value) for name, _, value in columns]
        status_columns = [(name, type_) for name, type_, _ in columns]
        status_assignment = ''.join(status_assignments)
    elif status:
        # old style: column name
        # stores all status as json in a single column
        name, type_, value = status_column(status, '*')
        status_columns = [(name, type_)]
        status_assignment = column_assignment(name, value)
    return (status_assignment, status_columns)


def hash_as_big_int(text):
    # Calculate a positive bigint hash, hence the 63-bit mask.
    return int(hashlib.sha1(text.encode()).hexdigest(), 16) & ((2**63)-1)


def set_pre_summary_info(summary, output):
    logging.debug(summary)
    output['total_rows'] = sum(summary.values())
    output['required_quota'] = sum(
        [summary[s] for s in ['new_geocoded', 'new_nongeocoded', 'changed_geocoded', 'changed_nongeocoded']])
    output['previously_geocoded'] = summary.get('previously_geocoded', 0)
    output['previously_failed'] = summary.get('previously_nongeocoded', 0)
    output['records_with_geometry'] = sum(
        summary[s] for s in ['new_geocoded', 'changed_geocoded', 'previously_geocoded'])


def set_post_summary_info(summary, result, output):
    if result and result.get('total_rows', 0) == 1:
        null_geom_count = result.get('rows')[0].get('count')
        geom_count = output['total_rows'] - null_geom_count
        output['final_records_with_geometry'] = geom_count
        # output['final_records_without_geometry'] = null_geom_count
        output['geocoded_increment'] = output['final_records_with_geometry'] - output['records_with_geometry']
        new_or_changed = sum([summary[s] for s in ['new_geocoded', 'changed_geocoded']])
        output['successfully_geocoded'] = output['geocoded_increment'] + new_or_changed
        output['failed_geocodings'] = output['required_quota'] - output['successfully_geocoded']


def list_difference(l1, l2):
    """list substraction compatible with Python2"""
    # return l1 - l2
    return list(set(l1) - set(l2))


def column_or_value_arg(arg, valid_columns=None):
    if arg is None:
        return None
    is_column = False
    if isinstance(arg, dict):
        invalid_keys = list_difference(arg.keys(), geocoding_constants.VALID_GEOCODE_KEYS)
        if any(invalid_keys):
            invalid_keys_list = ', '.join(list(invalid_keys))
            valid_keys_list = ', '.join(geocoding_constants.VALID_GEOCODE_KEYS)
            raise ValueError("Invalid key for argument {} valid keys are: {}".format(
                invalid_keys_list,
                valid_keys_list)
            )
        if len(arg.keys()) != 1:
            valid_keys_list = ', '.join(geocoding_constants.VALID_GEOCODE_KEYS)
            raise ValueError("Exactly one key of {} must be present in argument".format(valid_keys_list))
        key = list(arg.keys())[0]
        if key == geocoding_constants.GEOCODE_COLUMN_KEY:
            arg = arg[geocoding_constants.GEOCODE_COLUMN_KEY]
            is_column = True
        else:
            arg = "'{}'".format(arg[geocoding_constants.GEOCODE_VALUE_KEY])
    else:
        is_column = True
    if is_column and valid_columns:
        if arg not in valid_columns:
            raise ValueError("Argument is not a valid column name: {}".format(arg))
    return arg
