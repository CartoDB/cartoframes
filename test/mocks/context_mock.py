# -*- coding: utf-8 -*-

from cartoframes.auth import Credentials


class ContextMock():
    def __init__(self, username, api_key):
        self.is_org = False
        self.creds = Credentials(api_key=api_key, username=username)
        self.session = ''

    def get_default_schema(self):
        return 'public' if not self.is_org else self.creds.username

    def _get_bounds(self, layers):
        return {'west': None, 'south': None, 'east': None, 'north': None}
