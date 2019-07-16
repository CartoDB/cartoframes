# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.data.dataset about strategy changes"""
import unittest
import pandas as pd

from cartoframes.geojson import load_geojson
from mocks.dataset_mock import DatasetMock
from mocks.context_mock import ContextMock
from cartoframes.data.registry.dataframe_dataset import DataFrameDataset
from cartoframes.data.registry.table_dataset import TableDataset
from cartoframes.data.registry.query_dataset import QueryDataset


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
        dataset = DatasetMock(table_name, credentials=self.context)
        self.assertTrue(isinstance(dataset._strategy, TableDataset))
        self.assertTrue(dataset.is_remote())
        self.assertTrue(dataset.is_saved_in_carto)

    def test_dataset_from_table_after_download(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, credentials=self.context)
        self.assertTrue(isinstance(dataset._strategy, TableDataset))
        self.assertTrue(dataset.is_remote())
        self.assertTrue(dataset.is_saved_in_carto)
        dataset.download()
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertTrue(dataset.is_saved_in_carto)

    def test_dataset_from_table_after_upload(self):
        table_name = 'fake_table'
        dataset = DatasetMock(table_name, credentials=self.context)
        dataset.download()
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertTrue(dataset.is_saved_in_carto)
        dataset.upload(table_name='another_table')
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertEqual(dataset.table_name, 'another_table')
        self.assertTrue(dataset.is_saved_in_carto)

    def test_dataset_from_query(self):
        query = "SELECT 1"
        dataset = DatasetMock(query, credentials=self.context)
        self.assertTrue(isinstance(dataset._strategy, QueryDataset))
        self.assertTrue(dataset.is_remote())
        self.assertTrue(dataset.is_saved_in_carto)

    def test_dataset_from_query_after_download(self):
        query = "SELECT 1"
        dataset = DatasetMock(query, credentials=self.context)
        self.assertTrue(isinstance(dataset._strategy, QueryDataset))
        self.assertTrue(dataset.is_remote())
        self.assertTrue(dataset.is_saved_in_carto)
        dataset.download()
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertTrue(dataset.is_saved_in_carto)

    def test_dataset_from_query_and_upload(self):
        query = "SELECT 1"
        dataset = DatasetMock(query, credentials=self.context)
        self.assertTrue(isinstance(dataset._strategy, QueryDataset))
        self.assertTrue(dataset.is_remote())
        self.assertTrue(dataset.is_saved_in_carto)
        dataset.upload(table_name='another_table')
        self.assertTrue(isinstance(dataset._strategy, TableDataset))
        self.assertTrue(dataset.is_remote())
        self.assertEqual(dataset.table_name, 'another_table')
        self.assertTrue(dataset.is_saved_in_carto)

    def test_dataset_from_dataframe(self):
        df = pd.DataFrame({'column_name': [2]})
        dataset = DatasetMock(df)
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertFalse(dataset.is_saved_in_carto)

    def test_dataset_from_dataframe_upload(self):
        df = pd.DataFrame({'column_name': [2]})
        dataset = DatasetMock(df)
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertFalse(dataset.is_saved_in_carto)
        dataset.upload(table_name='another_table', credentials=self.context)
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertEqual(dataset.table_name, 'another_table')
        self.assertTrue(dataset.is_saved_in_carto)

    def test_dataset_from_dataframe_upload_append(self):
        df = pd.DataFrame({'column_name': [2]})
        dataset = DatasetMock(df)
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertFalse(dataset.is_saved_in_carto)
        dataset.upload(table_name='another_table', credentials=self.context, if_exists=DatasetMock.APPEND)
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertTrue(dataset.is_saved_in_carto)

    def test_dataset_from_geodataframe(self):
        gdf = load_geojson(self.test_geojson)
        dataset = DatasetMock(gdf)
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertFalse(dataset.is_saved_in_carto)

    def test_dataset_from_geojson(self):
        geojson = self.test_geojson
        dataset = DatasetMock(geojson)
        self.assertTrue(isinstance(dataset._strategy, DataFrameDataset))
        self.assertTrue(dataset.is_local())
        self.assertFalse(dataset.is_saved_in_carto)
