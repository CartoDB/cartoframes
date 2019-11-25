from . import geocoding_utils


class TableGeocodingLock:
    def __init__(self, execute_query, table_name):
        self._execute_query = execute_query
        text_id = 'carto-geocoder-{table_name}'.format(table_name=table_name)
        self.lock_id = geocoding_utils.hash_as_big_int(text_id)
        self.locked = False

    def __enter__(self):
        self.locked = geocoding_utils.lock(self._execute_query, self.lock_id)
        return self.locked

    def __exit__(self, type, value, traceback):
        if self.locked:
            geocoding_utils.unlock(self._execute_query, self.lock_id)
