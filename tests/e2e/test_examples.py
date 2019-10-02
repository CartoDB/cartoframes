# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.examples"""
import unittest

import pandas as pd
from cartoframes.examples import Examples


class TestExamples(unittest.TestCase):
    """Tests examples class"""

    def setUp(self):
        self.examples = Examples()

    def test_tables(self):
        """examples.tables"""
        tables = self.examples.tables()
        self.assertTrue(tables)

    def test_read_taxi(self):
        """examples.read_taxi"""
        from cartoframes.examples import read_taxi
        # method test
        taxi = self.examples.read_taxi()
        self.assertIsInstance(taxi, pd.DataFrame)
        self.assertGreater(taxi.shape[0], 0)

        # function test
        taxi = read_taxi()
        self.assertIsInstance(taxi, pd.DataFrame)
        self.assertGreater(taxi.shape[0], 0)

    def test_read_brooklyn_poverty(self):
        """examples.read_brooklyn_poverty"""
        from cartoframes.examples import read_brooklyn_poverty
        # method test
        bp = self.examples.read_brooklyn_poverty()
        self.assertIsInstance(bp, pd.DataFrame)
        self.assertGreaterEqual(bp.shape[0], 0)

        # function test
        bp = read_brooklyn_poverty()
        self.assertIsInstance(bp, pd.DataFrame)
        self.assertGreaterEqual(bp.shape[0], 0)

    def test_read_mcdonalds(self):
        """examples.read_mcdonalds"""
        from cartoframes.examples import read_mcdonalds_nyc
        # method test
        mcd = self.examples.read_mcdonalds_nyc()
        self.assertIsInstance(mcd, pd.DataFrame)
        self.assertGreater(mcd.shape[0], 0)

        # function test
        mcd = read_mcdonalds_nyc()
        self.assertIsInstance(mcd, pd.DataFrame)
        self.assertGreater(mcd.shape[0], 0)

    def test_read_nyc_census_tracts(self):
        """examples.read_nyc_census_tracts"""
        from cartoframes.examples import read_nyc_census_tracts
        # method test
        nycct = self.examples.read_nyc_census_tracts()
        self.assertIsInstance(nycct, pd.DataFrame)
        self.assertGreater(nycct.shape[0], 0)

        # function test
        nycct = read_nyc_census_tracts()
        self.assertIsInstance(nycct, pd.DataFrame)
        self.assertGreater(nycct.shape[0], 0)

    def test_read_nat(self):
        """examples.read_nat"""
        from cartoframes.examples import read_nat
        # method test
        nat = self.examples.read_nat()
        self.assertIsInstance(nat, pd.DataFrame)
        self.assertGreater(nat.shape[0], 0)

        # function test
        nat = read_nat()
        self.assertIsInstance(nat, pd.DataFrame)
        self.assertGreater(nat.shape[0], 0)
