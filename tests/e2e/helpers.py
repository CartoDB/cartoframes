"""Utility functions for cartoframes testing"""
import json
import logging
import os
import warnings

import pytest


class _UserUrlLoader:
    def user_url(self):
        user_url = None
        if os.environ.get('USERURL') is None:
            try:
                creds = json.loads(open('tests/e2e/secret.json').read())
                user_url = creds['USERURL']
            except Exception:
                warnings.warn('secret.json not found')

        if user_url in (None, ''):
            user_url = 'https://{username}.carto.com/'

        return user_url


QUOTAS = {}


def _update_quotas(service, quota):
    if service not in QUOTAS:
        QUOTAS[service] = {
            'initial': None,
            'final': None
        }
    QUOTAS[service]['final'] = quota
    if QUOTAS[service]['initial'] is None:
        QUOTAS[service]['initial'] = quota
    return quota


def _report_quotas():
    """Run pytest with options --log-level=info --log-cli-level=info
       to see this message about quota used during the tests
    """
    for service in QUOTAS:
        used_quota = QUOTAS[service]['final'] - QUOTAS[service]['initial']
        logging.info("TOTAL USED QUOTA for %s:  %d", service, used_quota)


class _ReportQuotas:
    @pytest.fixture(autouse=True, scope='class')
    def module_setup_teardown(self):
        yield
        _report_quotas()

    @classmethod
    def update_quotas(cls, service, quota):
        return _update_quotas(str(cls) + '_' + service, quota)
