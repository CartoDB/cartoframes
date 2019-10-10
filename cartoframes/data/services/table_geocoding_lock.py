from __future__ import absolute_import

import hashlib
import logging

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

def _hash_as_big_int(text):
    # Calculate a positive bigint hash, hence the 63-bit mask.
    return int(hashlib.sha1(text.encode()).hexdigest(), 16) & ((2**63)-1)

def _unlock(context, lock_id):
    logging.debug('UNLOCK %s' % lock_id)
    sql = 'select pg_advisory_unlock({id})'.format(id=lock_id)
    result = context.execute_query(sql)
    return result and result.get('rows', [])[0].get('pg_advisory_unlock')

def _lock(context, lock_id):
    sql = 'select pg_try_advisory_lock({id})'.format(id=lock_id)
    result = context.execute_query(sql)
    locked = result and result.get('rows', [])[0].get('pg_try_advisory_lock')
    logging.debug('LOCK %s : %s' % (lock_id, locked))
    return locked
