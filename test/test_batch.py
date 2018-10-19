"""Unit tests for cartoframes.batch"""
import unittest
import os
import sys
import json
import random
import warnings

import pandas as pd
from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
from carto.exceptions import CartoException
import cartoframes

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

class TestBatchJobStatus(unittest.TestCase, _UserUrlLoader):
    """Tests for cartoframes.BatchJobStatus"""
    def setUp(self):
        if (os.environ.get('APIKEY') is None or
                os.environ.get('USERNAME') is None):
            try:
                creds = json.loads(open('test/secret.json').read())
                self.apikey = creds['APIKEY']
                self.username = creds['USERNAME']
            except:  # noqa
                warnings.warn('Skipping CartoContext tests. To test it, '
                              'create a `secret.json` file in test/ by '
                              'renaming `secret.json.sample` to `secret.json` '
                              'and updating the credentials to match your '
                              'environment.')
                self.apikey = None
                self.username = None
        else:
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']

        self.user_url = self.user_url()

        if self.username and self.apikey:
            self.baseurl = self.user_url.format(
                username=self.username)
            self.auth_client = APIKeyAuthClient(base_url=self.baseurl,
                                                api_key=self.apikey)
            self.sql_client = SQLClient(self.auth_client)

        # sets skip value
        WILL_SKIP = self.apikey is None or self.username is None  # noqa: F841
        has_mpl = 'mpl' if os.environ.get('MPLBACKEND') else 'nonmpl'
        has_gpd = 'gpd' if os.environ.get('HAS_GEOPANDAS') else 'nongpd'
        buildnum = os.environ.get('TRAVIS_BUILD_NUMBER')
        pyver = sys.version[0:3].replace('.', '_')

        # for writing to carto
        self.test_write_lnglat_table = (
            'cf_test_write_lnglat_table_{ver}_{num}_{mpl}_{gpd}'.format(
                ver=pyver,
                num=buildnum,
                gpd=has_gpd,
                mpl=has_mpl))

    def tearDown(self):
        """restore to original state"""
        tables = (self.test_write_lnglat_table, )

        if self.apikey and self.baseurl:
            cc = cartoframes.CartoContext(base_url=self.baseurl,
                                          api_key=self.apikey)
            for table in tables:
                cc.delete(table)

    def test_batchjobstatus(self):
        """context.BatchJobStatus"""
        from cartoframes.batch import BatchJobStatus
        from cartoframes.context import MAX_ROWS_LNGLAT

        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        n_vals = MAX_ROWS_LNGLAT + 1
        df = pd.DataFrame({
            'lngvals': [random.random() for r in range(n_vals)],
            'latvals': [random.random() for r in range(n_vals)]
            })
        job = cc.write(df, self.test_write_lnglat_table,
                       lnglat=('lngvals', 'latvals'))

        self.assertIsInstance(job, cartoframes.context.BatchJobStatus)

        # no job exists for job_id 'foo'
        bjs = BatchJobStatus(cc, dict(job_id='foo', status='unknown'))
        with self.assertRaises(CartoException):
            bjs.status()

    def test_batchjobstatus_repr(self):
        """context.BatchJobStatus.__repr__"""
        from cartoframes.batch import BatchJobStatus
        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)
        bjs = BatchJobStatus(cc, dict(job_id='foo', status='unknown',
                                      created_at=None))
        self.assertMultiLineEqual(bjs.__repr__(),
                                  ("BatchJobStatus(job_id='foo', "
                                   "last_status='unknown', "
                                   "created_at='None')"))

    def test_batchjobstatus_methods(self):
        """context.BatchJobStatus methods"""
        from cartoframes.batch import BatchJobStatus
        from carto.sql import BatchSQLClient

        cc = cartoframes.CartoContext(base_url=self.baseurl,
                                      api_key=self.apikey)

        batch_client = BatchSQLClient(cc.auth_client)
        job_response = batch_client.create(['select 1', ])
        job_status = BatchJobStatus(cc, job_response)

        possible_status = ('pending', 'running', 'done',
                           'canceled', 'unknown', )
        self.assertTrue(job_status.get_status() in possible_status)
        job_status._set_status('foo')

        self.assertEqual(job_status.get_status(), 'foo')

        new_status = job_status.status()
        self.assertSetEqual(set(new_status.keys()),
                            {'status', 'updated_at', 'created_at'})

        # job_id as str
        str_bjs = BatchJobStatus(cc, 'foo')
        self.assertIsNone(str_bjs.get_status())
        self.assertEqual(str_bjs.job_id, 'foo')
