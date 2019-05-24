# -*- coding: utf-8 -*-

class CredsMock():
    def __init__(self, key=None, username=None):
        self._key = key
        self._username = username

    def username(self):
        return self._username

class ContextMock():
    def __init__(self, username, api_key):
        self.is_org = True
        self.creds = CredsMock(key=api_key, username=username)
