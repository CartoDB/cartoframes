"""Utility functions for cartoframes testing"""
import os
import json
import warnings


class _UserUrlLoader:
    def user_url(self):
        user_url = None
        if (os.environ.get('USERURL') is None):
            try:
                creds = json.loads(open('test/secret.json').read())
                user_url = creds['USERURL']
            except:  # noqa: E722
                warnings.warn('secret.json not found')

        if user_url in (None, ''):
            user_url = 'https://{username}.carto.com/'

        return user_url
