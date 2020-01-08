# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.client.DataObsClient"""

import os
import sys
import json
import pytest
import unittest
import warnings
import pandas as pd

from carto.exceptions import CartoException

from cartoframes import read_carto, delete_table
from cartoframes.auth import Credentials
from cartoframes.data.clients import DataObsClient, SQLClient
from cartoframes.data.clients.data_obs_client import get_countrytag
from cartoframes.utils.columns import normalize_name
from tests.e2e.helpers import _UserUrlLoader

warnings.filterwarnings('ignore')


@pytest.mark.skip()
class TestDataObsClient(unittest.TestCase, _UserUrlLoader):
    """Tests for cartoframes.client.DataObsClient"""

    def setUp(self):
        if (os.environ.get('APIKEY') is None or
                os.environ.get('USERNAME') is None):
            try:
                creds = json.loads(open('tests/e2e/secret.json').read())
                self.apikey = creds['APIKEY']
                self.username = creds['USERNAME']
            except Exception:
                warnings.warn("Skipping Context tests. To test it, "
                              "create a `secret.json` file in test/ by "
                              "renaming `secret.json.sample` to `secret.json` "
                              "and updating the credentials to match your "
                              "environment.")
                self.apikey = None
                self.username = None
        else:
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']

        self.base_url = self.user_url().format(username=self.username)
        self.credentials = Credentials(self.username, self.apikey, self.base_url)
        self.sql_client = SQLClient(self.credentials)

        # table naming info
        has_mpl = 'mpl' if os.environ.get('MPLBACKEND') else 'nonmpl'
        pyver = sys.version[0:3].replace('.', '_')
        buildnum = os.environ.get('TRAVIS_BUILD_NUMBER')

        test_slug = '{ver}_{num}_{mpl}'.format(
            ver=pyver, num=buildnum, mpl=has_mpl
        )

        # test tables
        self.test_read_table = 'cb_2013_us_csa_500k'
        self.valid_columns = set(['affgeoid', 'aland', 'awater', 'created_at',
                                  'csafp', 'geoid', 'lsad', 'name', 'the_geom',
                                  'updated_at'])
        # torque table
        self.test_point_table = 'tweets_obama'

        # for writing to carto
        self.test_write_table = normalize_name(
            'cf_test_table_{}'.format(test_slug)
        )

        self.mixed_case_table = normalize_name(
            'AbCdEfG_{}'.format(test_slug)
        )

        # for batch writing to carto
        self.test_write_batch_table = normalize_name(
            'cf_testbatch_table_{}'.format(test_slug)
        )

        self.test_write_lnglat_table = normalize_name(
            'cf_testwrite_lnglat_table_{}'.format(test_slug)
        )

        self.write_named_index = normalize_name(
            'cf_testwrite_non_default_index_{}'.format(test_slug)
        )

        # for queries
        self.test_query_table = normalize_name(
            'cf_testquery_table_{}'.format(test_slug)
        )

        self.test_delete_table = normalize_name(
            'cf_testdelete_table_{}'.format(test_slug)
        )

        # for data observatory
        self.test_data_table = 'carto_usa_offices'

    def tearDown(self):
        """restore to original state"""
        tables = (self.test_write_table,
                  self.test_write_batch_table,
                  self.test_write_lnglat_table,
                  self.test_query_table,
                  self.mixed_case_table.lower(),
                  self.write_named_index, )
        sql_drop = 'DROP TABLE IF EXISTS {};'

        for table in tables:
            try:
                delete_table(table, credentials=self.credentials)
                self.sql_client.query(sql_drop.format(table))
            except CartoException:
                warnings.warn('Error deleting tables')

    def test_boundaries(self):
        """DataObsClient.boundaries"""
        do = DataObsClient(self.credentials)

        # all boundary metadata
        boundary_meta = do.boundaries()
        self.assertTrue(boundary_meta.shape[0] > 0,
                        msg='has non-zero number of boundaries')
        meta_cols = set(('geom_id', 'geom_tags', 'geom_type', ))
        self.assertTrue(meta_cols & set(boundary_meta.columns))

        # boundary metadata with correct timespan
        meta_2015 = do.boundaries(timespan='2015')
        self.assertTrue(meta_2015[meta_2015.valid_timespan].shape[0] > 0)

        # test for no data with an incorrect or invalid timespan
        meta_9999 = do.boundaries(timespan='invalid_timespan')
        self.assertTrue(meta_9999[meta_9999.valid_timespan].shape[0] == 0)

        # boundary metadata in a region
        regions = (
            self.test_read_table,
            self.test_data_table,
            [5.9559111595, 45.8179931641, 10.4920501709, 47.808380127],
            'Australia', )
        for region in regions:
            boundary_meta = do.boundaries(region=region)
            self.assertTrue(meta_cols & set(boundary_meta.columns))
            self.assertTrue(boundary_meta.shape[0] > 0,
                            msg='has non-zero number of boundaries')

        #  boundaries for world
        boundaries = do.boundaries(boundary='us.census.tiger.state')
        self.assertTrue(boundaries.shape[0] > 0)
        self.assertEqual(boundaries.shape[1], 2)
        self.assertSetEqual(set(('the_geom', 'geom_refs', )),
                            set(boundaries.columns))

        # boundaries for region
        boundaries = ('us.census.tiger.state', )
        for b in boundaries:
            geoms = do.boundaries(
                boundary=b,
                region=self.test_data_table)
            self.assertTrue(geoms.shape[0] > 0)
            self.assertEqual(geoms.shape[1], 2)
            self.assertSetEqual(set(('the_geom', 'geom_refs', )),
                                set(geoms.columns))

        # presence or lack of clipped boundaries
        nonclipped = (True, False, )
        for tf in nonclipped:
            meta = do.boundaries(include_nonclipped=tf)
            self.assertEqual(
                'us.census.tiger.state' in set(meta.geom_id),
                tf
            )

        with self.assertRaises(ValueError):
            do.boundaries(region=[1, 2, 3])

        with self.assertRaises(ValueError):
            do.boundaries(region=10)

    def test_discovery(self):
        """DataObsClient.discovery"""
        do = DataObsClient(self.credentials)

        meta = do.discovery(self.test_read_table,
                            keywords=('poverty', ),
                            time=('2010 - 2014', ))
        meta_columns = set((
            'denom_aggregate', 'denom_colname', 'denom_description',
            'denom_geomref_colname', 'denom_id', 'denom_name',
            'denom_reltype', 'denom_t_description', 'denom_tablename',
            'denom_type', 'geom_colname', 'geom_description',
            'geom_geomref_colname', 'geom_id', 'geom_name',
            'geom_t_description', 'geom_tablename', 'geom_timespan',
            'geom_type', 'id', 'max_score_rank', 'max_timespan_rank',
            'normalization', 'num_geoms', 'numer_aggregate',
            'numer_colname', 'numer_description', 'numer_geomref_colname',
            'numer_id', 'numer_name', 'numer_t_description',
            'numer_tablename', 'numer_timespan', 'numer_type', 'score',
            'score_rank', 'score_rownum', 'suggested_name', 'target_area',
            'target_geoms', 'timespan_rank', 'timespan_rownum'))
        self.assertSetEqual(set(meta.columns), meta_columns,
                            msg='metadata columns are all there')
        self.assertTrue((meta['numer_timespan'] == '2010 - 2014').all())
        self.assertTrue((meta['numer_description'].str.contains('poverty')).all())

        # test region = list of lng/lats
        with self.assertRaises(ValueError):
            do.discovery([1, 2, 3])

        switzerland = [5.9559111595, 45.8179931641,
                       10.4920501709, 47.808380127]
        dd = do.discovery(switzerland, keywords='freight', time='2010')
        self.assertEqual(dd['numer_id'][0], 'eu.eurostat.tgs00078')

        dd = do.discovery('Australia',
                          regex='.*Torres Strait Islander.*')
        for nid in dd['numer_id'].values:
            self.assertRegexpMatches(nid, r'^au\.data\.B01_Indig_[A-Za-z_]+Torres_St[A-Za-z_]+[FMP]$')

        with self.assertRaises(CartoException):
            do.discovery('non_existent_table_abcdefg')

        dd = do.discovery('United States',
                          boundaries='us.epa.huc.hydro_unit',
                          time=('2006', '2010', ))
        self.assertTrue(dd.shape[0] >= 1)

        poverty = do.discovery(
            'United States',
            boundaries='us.census.tiger.census_tract',
            keywords=['poverty status', ],
            time='2011 - 2015',
            include_quantiles=False)
        df_quantiles = poverty[poverty.numer_aggregate == 'quantile']
        self.assertEqual(df_quantiles.shape[0], 0)

        poverty = do.discovery(
            'United States',
            boundaries='us.census.tiger.census_tract',
            keywords=['poverty status', ],
            time='2011 - 2015',
            include_quantiles=True)
        df_quantiles = poverty[poverty.numer_aggregate == 'quantile']
        self.assertTrue(df_quantiles.shape[0] > 0)

    def test_augment(self):
        """DataObsClient.augment"""
        do = DataObsClient(self.credentials)

        meta = do.discovery(self.test_read_table,
                            keywords=('poverty', ),
                            time=('2010 - 2014', ))
        gdf = do.augment(self.test_data_table, meta)
        anscols = set(meta['suggested_name'])
        origcols = set(
            read_carto(self.test_data_table, credentials=self.credentials, limit=1, decode_geom=True).columns)
        self.assertSetEqual(anscols, set(gdf.columns) - origcols - {'the_geom', 'cartodb_id'})

        meta = [{'numer_id': 'us.census.acs.B19013001',
                 'geom_id': 'us.census.tiger.block_group',
                 'numer_timespan': '2011 - 2015'}, ]
        gdf = do.augment(self.test_data_table, meta)
        self.assertSetEqual(set(('median_income_2011_2015', )),
                            set(gdf.columns) - origcols - {'the_geom', 'cartodb_id'})

        with self.assertRaises(ValueError, msg='no measures'):
            meta = do.discovery('United States', keywords='not a measure')
            do.augment(self.test_read_table, meta)

        with self.assertRaises(ValueError, msg='too many metadata measures'):
            # returns ~180 measures
            meta = do.discovery(region='united states',
                                keywords='education')
            do.augment(self.test_read_table, meta)

    @pytest.mark.skip()
    def test_augment_with_persist_as(self):
        """DataObsClient.augment with persist_as"""
        do = DataObsClient(self.credentials)

        meta = do.discovery(self.test_read_table,
                            keywords=('poverty', ),
                            time=('2010 - 2014', ))
        gdf = do.augment(self.test_data_table, meta)
        anscols = set(meta['suggested_name'])
        origcols = set(
            read_carto(self.test_data_table, credentials=self.credentials, limit=1, decode_geom=True).columns)
        self.assertSetEqual(anscols, set(gdf.columns) - origcols - {'the_geom', 'cartodb_id'})

        meta = [{'numer_id': 'us.census.acs.B19013001',
                 'geom_id': 'us.census.tiger.block_group',
                 'numer_timespan': '2011 - 2015'}, ]
        gdf = do.augment(self.test_data_table, meta, persist_as=self.test_write_table)
        self.assertSetEqual(set(('median_income_2011_2015', )),
                            set(gdf.columns) - origcols - {'the_geom', 'cartodb_id'})
        self.assertEqual(gdf.index.name, 'cartodb_id')
        self.assertEqual(gdf.index.dtype, 'int64')

        df = read_carto(self.test_write_table, credentials=self.credentials, decode_geom=False)

        self.assertEqual(df.index.name, 'cartodb_id')
        self.assertEqual(df.index.dtype, 'int64')

        # same number of rows
        self.assertEqual(len(df), len(gdf),
                         msg='Expected number or rows')

        # same type of object
        self.assertIsInstance(df, pd.DataFrame,
                              'Should be a pandas DataFrame')
        # same column names
        self.assertSetEqual(set(gdf.columns.values),
                            set(df.columns.values),
                            msg='Should have the columns requested')

        # should have exected schema
        self.assertEqual(
            sorted(tuple(str(d) for d in df.dtypes)),
            sorted(tuple(str(d) for d in gdf.dtypes)),
            msg='Should have same schema/types'
        )

    def test_augment_column_name_collision(self):
        """DataObsClient.augment column name collision"""
        dup_col = 'female_third_level_studies_2011_by_female_pop'
        self.sql_client.query(
            """
            create table {table} as (
                select cdb_latlng(40.4165,-3.70256) the_geom,
                       1 {dup_col})
            """.format(
                dup_col=dup_col,
                table=self.test_write_table
            )
        )
        self.sql_client.query(
            "select cdb_cartodbfytable('public', '{table}')".format(
                table=self.test_write_table
            )
        )

        do = DataObsClient(self.credentials)
        meta = do.discovery(region=self.test_write_table, keywords='female')
        meta = meta[meta.suggested_name == dup_col]
        gdf = do.augment(
            self.test_write_table,
            meta[meta.suggested_name == dup_col]
        )

        self.assertIn('_' + dup_col, gdf.keys())

    def test_get_countrytag(self):
        valid_regions = ('Australia', 'Brasil', 'EU', 'España', 'U.K.', )
        valid_answers = ['section/tags.{c}'.format(c=c)
                         for c in ('au', 'br', 'eu', 'spain', 'uk', )]
        invalid_regions = ('USofA', None, '', 'Jupiter', )

        for idx, r in enumerate(valid_regions):
            self.assertEqual(get_countrytag(r.lower()), valid_answers[idx])

        for r in invalid_regions:
            with self.assertRaises(ValueError):
                get_countrytag(r)
