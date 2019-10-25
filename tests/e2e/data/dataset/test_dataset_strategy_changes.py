# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.data.dataset about strategy changes"""
import unittest

import pandas as pd

from cartoframes.auth import Credentials
from cartoframes.data.dataset.registry.strategies_registry import StrategiesRegistry
from cartoframes.data.dataset.registry.dataframe_dataset import \
    DataFrameDataset
from cartoframes.data.dataset.registry.query_dataset import QueryDataset
from cartoframes.data.dataset.registry.table_dataset import TableDataset
from cartoframes.lib import context
from cartoframes.utils.utils import load_geojson
from tests.unit.mocks.context_mock import ContextMock
from tests.unit.mocks.dataset_mock import DatasetMock


class TestDatasetStrategyChanges(unittest.TestCase):
    def setUp(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.credentials = Credentials(username=self.username, api_key=self.api_key)

        self.test_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            -3.1640625,
                            42.032974332441405
                        ]
                    }
                }
            ]
        }

        self._context_mock = ContextMock()
        # Mock create_context method
        self.original_create_context = context.create_context
        context.create_context = lambda c: self._context_mock

    def tearDown(self):
        StrategiesRegistry.instance = None
        context.create_context = self.original_create_context

    def test_dataset_from_table(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, credentials=self.credentials)
        self.assertTrue(isinstance(dataset._strategy, TableDataset))
        self.assertTrue(dataset.is_remote())

    def test_dataset_from_query(self):
        query = "SELECT 1"
        dataset = DatasetMock(query, credentials=self.credentials)
        self.assertTrue(isinstance(dataset._strategy, QueryDataset))
        self.assertTrue(dataset.is_remote())

    def test_dataset_from_geodataframe(self):
        gdf = load_geojson(self.test_geojson)
        dataset = DatasetMock(gdf)
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())

    def test_dataset_from_geojson(self):
        geojson = self.test_geojson
        dataset = DatasetMock(geojson)
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())

    def test_local_dataset_upload_returns_table_dataset(self):
        gdf = load_geojson(self.test_geojson)
        local_dataset = DatasetMock(gdf)
        table_dataset = local_dataset.upload(table_name='fake_table', credentials=self.credentials)
        self.assertTrue(isinstance(local_dataset._strategy, DataFrameDataset))
        self.assertTrue(isinstance(table_dataset._strategy, TableDataset))

    def test_table_dataset_download_returns_dataframe(self):
        table_dataset = DatasetMock('fake_table', credentials=self.credentials)
        df = table_dataset.download()
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertTrue(df.equals(table_dataset.dataframe))
        self.assertTrue(isinstance(table_dataset._strategy, TableDataset))

    def test_query_dataset_download_returns_dataframe(self):
        query = 'SELECT * FROM fake_table'
        query_dataset = DatasetMock(query, credentials=self.credentials)
        df = query_dataset.download()
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertTrue(df.equals(query_dataset.dataframe))
        self.assertTrue(isinstance(query_dataset._strategy, QueryDataset))
