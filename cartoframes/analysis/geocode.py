from __future__ import absolute_import

import re
import hashlib
import logging

from .. import context
from ..auth import get_default_credentials
from carto.exceptions import CartoException

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


class table_geocoding_lock:
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


def _exists_hash_query(table):
    return """
      SELECT TRUE FROM pg_catalog.pg_attribute a
      WHERE
        a.attname = '{hash_column}'
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
        hash_column=HASH_COLUMN
    )


def _prior_summary_query(table, street, city, state, country):
    hash_expression = _hash_expr(street, city, state, country)
    return """
      SELECT
        CASE WHEN {hash_column} IS NULL THEN
          CASE WHEN the_geom IS NULL THEN 'nn' ELSE 'ng' END
        WHEN {hash_column} <> {hash_expression} THEN
          CASE WHEN the_geom IS NULL THEN 'cn' ELSE 'cg' END
        ELSE
          CASE WHEN the_geom IS NULL THEN 'pn' ELSE 'pg' END
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
        CASE WHEN the_geom IS NULL THEN 'nn' ELSE 'ng' END AS gc_state,
        COUNT(*) AS count
      FROM {table}
      GROUP BY gc_state
    """.format(
        table=table,
        hash_expression=hash_expression,
        hash_column=HASH_COLUMN
    )


def _posterior_summary_query(table, street, city, state, country):
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
            the_geom_webmercator = CASE
              WHEN _g.the_geom IS NULL THEN NULL
              ELSE ST_Transform(_g.the_geom, 3857)
            END,
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


class GeocodeAnalysis(object):

    def __init__(self, credentials=None):
        self._credentials = credentials or get_default_credentials()
        self._context = context.create_context(self._credentials)

    def preview(self, dataset, street, city=None, state=None, country=None, metadata=None):
        return self.geocode(dataset, street, city=city, state=state, country=country, metadata=metadata, dry=True)

    def geocode(self, dataset, street, city=None, state=None, country=None, metadata=None, dry=None):
        # Geocode rows not already geocoded in a dataset'
        # response = self._context.execute_query(query)
        # self._context.execute_long_running_query(query)
        # response.get('rows')
        # rows[0].get('column')

        logging.info('dataset = "%s"' % dataset.table_name)
        logging.info('street = "%s"' % street)
        logging.info('city = "%s"' % city)
        logging.info('state = "%s"' % state)
        logging.info('country = "%s"' % country)
        logging.info('metadata = "%s"' % metadata)
        logging.info('dry = "%s"' % dry)


        if not dataset.is_saved_in_carto:  # dataset.is_local()
            # TODO: handle this either by uploading the dataset,
            # uploading to a temporary table or geocoding addresses per row
            raise CartoException('Your data is not synchronized with CARTO. '
                                 'First of all, you should call the Dataset.upload() method '
                                 'to save your data in CARTO.'
                                 'Geocoding is supported only for synchronized data.')
        if dataset.table_name is None:
            # TODO: how should we support this case?
            raise CartoException('Geocoding is supported only for table datasets.')

        output = {}

        summary = {s: 0 for s in ['ng', 'nn', 'cg', 'cn', 'pg', 'pn']}
        # Summary keys:
        # ng (new-geocoded), nn (new-non-geocoded)
        # cg (changed-geocoded), cn (changed-non-geocoded)
        # ng (new-geocoded), nn (new-non-geocoded)
        # pg (previously-geocoded), pn (previously-non-geocoded)

        # TODO: Use a single transaction so that reported changes (posterior - prior queries)
        # are only caused by the geocoding process. Note that no rollback should be
        # performed once the geocoding update is executed, since
        # quota spent by the Dataservices function would not be rolled back;
        # hence a Python `with` statement is not used here.
        # transaction = connection.begin()

        result = self._execute_prior_summary(dataset.table_name, street, city, state, country)
        if result:
            for row in result.get('rows'):
                gc_state = row.get('gc_state')
                count = row.get('count')
                summary[gc_state] = count

        logging.debug(summary)
        output['total_rows'] = sum(summary.values())
        # TODO: either report new (ng+nn) and changed (cg+cn) records, or we could
        # reduce the states by merging ng+cg, nn+nn
        output['required_quota'] = sum([summary[s] for s in ['ng', 'nn', 'cg', 'cn']])
        output['previously_geocoded'] = summary.get('pg', 0)
        output['previously_failed'] = summary.get('pn', 0)
        output['records_with_geometry'] = sum([summary[s] for s in ['ng', 'cg', 'pg']])
        # output['records_without_geometry'] = sum([summary[s] for s in ['nn', 'cn', 'pn']])

        aborted = False

        if output['required_quota'] > 0 and not dry:
            with table_geocoding_lock(self._context, dataset.table_name) as locked:
                if not locked:
                    output['error'] = 'The table is already being geocoded'
                    output['aborted'] = aborted = True
                else:
                    # Create column to store input search hash
                    logging.info("Adding column {} if needed".format(HASH_COLUMN))
                    self._context.execute_query(
                        "ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {hash_column} text;"
                        .format(table=dataset.table_name, hash_column=HASH_COLUMN)
                    )

                    sql = _geocode_query(dataset.table_name, street, city, state, country, metadata)
                    logging.debug("Executing query: %s" % sql)
                    result = None
                    try:
                        result = self._context.execute_long_running_query(sql)
                    except Exception as err:
                        logging.error(err)
                        msg = str(err)
                        output['error'] = msg
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
                sql = _posterior_summary_query(dataset.table_name, street, city, state, country)
                logging.debug("Executing result summary query: %s" % sql)
                result = self._context.execute_query(sql)
                if result and result.get('total_rows', 0) == 1:
                    null_geom_count = result.get('rows')[0].get('count')
                    geom_count = output['total_rows'] - null_geom_count
                    output['final_records_with_geometry'] = geom_count
                    # output['final_records_without_geometry'] = null_geom_count
                    output['geocoded_increment'] = output['final_records_with_geometry'] - output['records_with_geometry']
                    output['successfully_geocoded'] = output['geocoded_increment'] + sum([summary[s] for s in ['ng', 'cg']])
                    output['failed_geocodings'] = output['required_quota'] - output['successfully_geocoded']

        if not aborted:
            # TODO
            # transaction.commit()
            pass

        return output  # TODO: GeocodeResult object

    def _execute_prior_summary(self, dataset_name, street, city, state, country):
        sql = _exists_hash_query(dataset_name)
        logging.debug("Executing check first time query: %s" % sql)
        result = self._context.execute_query(sql)
        if not result or result.get('total_rows', 0) == 0:
            sql = _first_time_summary_query(dataset_name, street, city, state, country)
            logging.debug("Executing first time summary query: %s" % sql)
        else:
            sql = _prior_summary_query(dataset_name, street, city, state, country)
            logging.debug("Executing summary query: %s" % sql)
        return self._context.execute_query(sql)
