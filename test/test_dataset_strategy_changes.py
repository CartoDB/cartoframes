# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.data.dataset about strategy changes"""
import unittest
import pandas as pd

from cartoframes.geojson import load_geojson
from mocks.dataset_mock import DatasetMock
from mocks.context_mock import ContextMock
from cartoframes.data.dataframe_dataset import DataFrameDataset
from cartoframes.data.table_dataset import TableDataset
from cartoframes.data.query_dataset import QueryDataset

class TestDatasetStrategyChanges(unittest.TestCase):
    def setUp(self):
        self.username = 'fake_username'
        self.api_key = 'fake_api_key'
        self.context = ContextMock(username=self.username, api_key=self.api_key)

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

    def test_dataset_from_table(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, context=self.context)
        self.assertEqual(isinstance(dataset._strategy, TableDataset), True)

    def test_dataset_from_table_after_download(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, context=self.context)
        self.assertEqual(isinstance(dataset._strategy, TableDataset), True)
        dataset.download()
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)

    def test_dataset_from_table_after_upload(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, context=self.context)
        dataset.download()
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)
        dataset.upload(table_name='another_table')
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)
        self.assertEqual(dataset.table_name, 'another_table')

    def test_dataset_from_query(self):
        query = "SELECT 1"
        dataset = DatasetMock(query, context=self.context)
        self.assertEqual(isinstance(dataset._strategy, QueryDataset), True)

    def test_dataset_from_query_after_download(self):
        query = "SELECT 1"
        dataset = DatasetMock(query, context=self.context)
        self.assertEqual(isinstance(dataset._strategy, QueryDataset), True)
        dataset.download()
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)

    def test_dataset_from_query_and_upload(self):
        query = "SELECT 1"
        dataset = DatasetMock(query, context=self.context)
        self.assertEqual(isinstance(dataset._strategy, QueryDataset), True)
        dataset.upload(table_name='another_table')
        self.assertEqual(isinstance(dataset._strategy, TableDataset), True)
        self.assertEqual(dataset.table_name, 'another_table')

    def test_dataset_from_dataframe(self):
        df = pd.DataFrame({'column_name': [2]})
        dataset = DatasetMock(df)
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)

    def test_dataset_from_dataframe_upload(self):
        df = pd.DataFrame({'column_name': [2]})
        dataset = DatasetMock(df)
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)
        dataset.upload(table_name='another_table', context=self.context)
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)
        self.assertEqual(dataset.table_name, 'another_table')

    def test_dataset_from_dataframe_upload_append(self):
        df = pd.DataFrame({'column_name': [2]})
        dataset = DatasetMock(df)
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)
        dataset.upload(table_name='another_table', context=self.context, if_exists=DatasetMock.APPEND)
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)

    def test_dataset_from_geodataframe(self):
        gdf = load_geojson(self.test_geojson)
        dataset = DatasetMock(gdf)
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)

    def test_dataset_from_geojson(self):
        geojson = self.test_geojson
        dataset = DatasetMock(geojson)
        self.assertEqual(isinstance(dataset._strategy, DataFrameDataset), True)
