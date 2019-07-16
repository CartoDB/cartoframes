# -*- coding: utf-8 -*-


class CredsMock():
    def __init__(self, key=None, username=None):
        self._key = key
        self._username = username

    def username(self):
        return self._username

    def key(self):
        return self._key

    def base_url(self):
        return 'https://{}.carto.com/'.format(self._username)


class ContextMock():
    def __init__(self, username, api_key):
        self.is_org = True
        self.creds = CredsMock(key=api_key, username=username)
        self.version = ''
        self.session = ''

    def get_default_schema(self):
        return self.creds.username() or 'public'

    def _get_bounds(self, layers):
        return {'west': None, 'south': None, 'east': None, 'north': None}
