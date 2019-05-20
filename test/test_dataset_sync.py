# -*- coding: utf-8 -*-

"""Unit tests for cartoframes.dataset about is_sync prop"""
import unittest
import os
import json
import warnings

from cartoframes.context import CartoContext
from cartoframes.dataset import Dataset
from cartoframes.geojson import load_geojson

from utils import _UserUrlLoader

warnings.filterwarnings("ignore")

class TestDatasetSync(unittest.TestCase, _UserUrlLoader):
    def setUp(self):
        if (os.environ.get('APIKEY') is None or
                os.environ.get('USERNAME') is None):
            try:
                creds = json.loads(open('test/secret.json').read())
                self.apikey = creds['APIKEY']
                self.username = creds['USERNAME']
            except:  # noqa: E722
                warnings.warn("Skipping CartoContext tests. To test it, "
                              "create a `secret.json` file in test/ by "
                              "renaming `secret.json.sample` to `secret.json` "
                              "and updating the credentials to match your "
                              "environment.")
                self.apikey = None
                self.username = None
        else:
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']

        self.baseurl = self.user_url().format(username=self.username)
        self.cc = CartoContext(base_url=self.baseurl, api_key=self.apikey)

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

        def mock_download(self):
            self.df = 4
            return self.df
        Dataset.download = mock_download

        def mock_copyfrom(self, _):
            return True
        Dataset._copyfrom = mock_copyfrom

        def mock_create_table(self, _):
            return True
        Dataset._create_table = mock_create_table

        def mock_create_table_from_query(self):
            return True
        Dataset._create_table_from_query = mock_create_table_from_query

        def mock_exists(self):
            return False
        Dataset.exists = mock_exists


    def test_dataset_sync_from_table(self):
        table_name = 'fake_table'
        dataset = Dataset.from_table(table_name=table_name, context=self.cc)
        self.assertEqual(dataset.is_sync, True)

    def test_dataset_not_sync_from_modified_table(self):
        table_name = 'fake_table'
        dataset = Dataset.from_table(table_name=table_name, context=self.cc)
        dataset.table_name = 'another_table'
        self.assertEqual(dataset.is_sync, False)

    def test_dataset_not_sync_from_modified_schema(self):
        table_name = 'fake_table'
        dataset = Dataset.from_table(table_name=table_name, context=self.cc)
        dataset.schema = 'another_schema'
        self.assertEqual(dataset.is_sync, False)

    def test_dataset_sync_from_table_after_download(self):
        table_name = 'fake_table'
        dataset = Dataset.from_table(table_name=table_name, context=self.cc)
        dataset.download()
        self.assertEqual(dataset.is_sync, True)

    def test_dataset_sync_from_table_after_upload(self):
        table_name = 'fake_table'
        dataset = Dataset.from_table(table_name=table_name, context=self.cc)
        dataset.download()
        dataset.upload(table_name='another_table')
        self.assertEqual(dataset.is_sync, True)
        self.assertEqual(dataset.table_name, 'another_table')

    def test_dataset_not_sync_from_query(self):
        query = "SELECT 1"
        dataset = Dataset.from_query(query=query, context=self.cc)
        self.assertEqual(dataset.is_sync, False)

    def test_dataset_not_sync_from_dataframe(self):
        df = load_geojson(self.test_geojson)
        dataset = Dataset.from_dataframe(df=df)
        self.assertEqual(dataset.is_sync, False)

    def test_dataset_not_sync_from_geodataframe(self):
        gdf = load_geojson(self.test_geojson)
        dataset = Dataset.from_geodataframe(gdf=gdf)
        self.assertEqual(dataset.is_sync, False)

    def test_dataset_not_sync_from_geojson(self):
        geojson = self.test_geojson
        dataset = Dataset.from_geojson(geojson=geojson)
        self.assertEqual(dataset.is_sync, False)
