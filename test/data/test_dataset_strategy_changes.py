# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.data.dataset about strategy changes"""
import unittest
import pandas as pd

from cartoframes.auth import Credentials
from cartoframes.utils import load_geojson
from cartoframes.data import StrategiesRegistry
from cartoframes.data.registry.dataframe_dataset import DataFrameDataset
from cartoframes.data.registry.table_dataset import TableDataset
from cartoframes.data.registry.query_dataset import QueryDataset
from cartoframes import context

from ..mocks.dataset_mock import DatasetMock
from ..mocks.context_mock import ContextMock


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
