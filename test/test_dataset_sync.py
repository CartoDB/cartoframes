# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.data about _is_saved_in_carto prop"""
import unittest
import pandas as pd

from cartoframes.geojson import load_geojson
from mocks.dataset_mock import DatasetMock
from mocks.context_mock import ContextMock


class TestDatasetSync(unittest.TestCase):
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

    def test_dataset_sync_from_table(self):
        table_name = 'fake_table'
        dataset = DatasetMock.from_table(table_name=table_name, context=self.context)
        self.assertEqual(dataset._is_saved_in_carto, True)

    def test_dataset_sync_from_table_after_download(self):
        table_name = 'fake_table'
        dataset = DatasetMock.from_table(table_name=table_name, context=self.context)
        dataset.download()
        self.assertEqual(dataset._is_saved_in_carto, True)

    def test_dataset_sync_from_table_after_upload(self):
        table_name = 'fake_table'
        dataset = DatasetMock.from_table(table_name=table_name, context=self.context)
        dataset.download()
        dataset.upload(table_name='another_table')
        self.assertEqual(dataset._is_saved_in_carto, True)
        self.assertEqual(dataset.table_name, 'another_table')

    def test_dataset_not_sync_from_query(self):
        query = "SELECT 1"
        dataset = DatasetMock.from_query(query=query, context=self.context)
        self.assertEqual(dataset._is_saved_in_carto, True)

    def test_dataset_sync_from_query_and_upload(self):
        query = "SELECT 1"
        dataset = DatasetMock.from_query(query=query, context=self.context)
        dataset.upload(table_name='another_table')
        self.assertEqual(dataset._is_saved_in_carto, True)
        self.assertEqual(dataset.table_name, 'another_table')

    def test_dataset_not_sync_from_dataframe(self):
        df = pd.DataFrame({'column_name': [2]})
        dataset = DatasetMock.from_dataframe(df=df)
        self.assertEqual(dataset._is_saved_in_carto, False)

    def test_dataset_sync_from_dataframe_upload(self):
        df = pd.DataFrame({'column_name': [2]})
        dataset = DatasetMock.from_dataframe(df=df)
        dataset.upload(table_name='another_table', context=self.context)
        self.assertEqual(dataset._is_saved_in_carto, True)
        self.assertEqual(dataset.table_name, 'another_table')

    def test_dataset_not_sync_from_dataframe_upload_append(self):
        df = pd.DataFrame({'column_name': [2]})
        dataset = DatasetMock.from_dataframe(df=df)
        dataset.upload(table_name='another_table', context=self.context, if_exists=DatasetMock.APPEND)
        self.assertEqual(dataset._is_saved_in_carto, False)

    def test_dataset_not_sync_from_geodataframe(self):
        gdf = load_geojson(self.test_geojson)
        dataset = DatasetMock.from_geodataframe(gdf=gdf)
        self.assertEqual(dataset._is_saved_in_carto, False)

    def test_dataset_not_sync_from_geojson(self):
        geojson = self.test_geojson
        dataset = DatasetMock.from_geojson(geojson=geojson)
        self.assertEqual(dataset._is_saved_in_carto, False)
