import unittest
import pandas as pd

from cartoframes.data.enrichment.enrichment_service import _prepare_data, _upload_dataframe, _enrichment_query, \
    _execute_enrichment, _get_bigquery_client
from cartoframes.data import Dataset
from cartoframes.data.clients.bigquery_client import BigQueryClient

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestEnrichmentService(unittest.TestCase):
    def setUp(self):
        self.original_init_client = BigQueryClient._init_client
        BigQueryClient._init_client = Mock(return_value=True)

    def tearDown(self):
        BigQueryClient._init_client = self.original_init_client

    def test_prepare_data(self):
        geom_column = 'the_geom'
        df = pd.DataFrame([[1, 'POINT (1 1)']], columns=['cartodb_id', geom_column])
        ds = Dataset(df)

        expected_df = pd.DataFrame([[1, '{"coordinates": [1.0, 1.0], "type": "Point"}', 0]], columns=['cartodb_id', geom_column, 'enrichment_id'])

        result = _prepare_data(ds, geom_column)
        self.assertTrue(result.equals(expected_df))
        result = _prepare_data(df, geom_column)
        self.assertTrue(result.equals(expected_df))

    def test_upload_dataframe(self):
        expected_project = 'carto-do-customers'
        credentails = True
        user_dataset = 'test_dataset'
        ttl = 1
        geom_column = 'the_geom'
        data_copy = pd.DataFrame([[1, '{"coordinates": [1.0, 1.0], "type": "Point"}', 0]], columns=['cartodb_id', geom_column, 'enrichment_id'])
        expected_schema = {'enrichment_id': 'INTEGER', 'the_geom': 'GEOGRAPHY'}
        expected_data_copy = pd.DataFrame([['{"coordinates": [1.0, 1.0], "type": "Point"}', 0]], columns=[geom_column, 'enrichment_id'])

        # mock
        def assert_upload_dataframe(_, dataframe, schema, tablename, project, dataset, ttl_days=None):
            assert dataframe.equals(expected_data_copy)
            assert schema == expected_schema
            assert isinstance(tablename, str) and len(tablename) > 0
            assert project == expected_project
            assert dataset == user_dataset
            assert ttl_days == ttl

        original = BigQueryClient.upload_dataframe
        BigQueryClient.upload_dataframe = assert_upload_dataframe

        bq_client = _get_bigquery_client(expected_project, credentails)

        _upload_dataframe(bq_client, user_dataset, data_copy, geom_column)

        BigQueryClient.upload_dataframe = original

    def test_enrichment_query(self):
        pass

    def test_execute_enrichment(self):
        pass
