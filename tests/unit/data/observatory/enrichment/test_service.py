import pandas as pd
from shapely.geometry.point import Point

from cartoframes.data import Dataset
from cartoframes.data.clients.bigquery_client import BigQueryClient
from cartoframes.data.observatory.enrichment.enrichment_service import EnrichmentService
from cartoframes.data.observatory.catalog import _get_bigquery_client

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestEnrichmentService(object):
    def setup_method(self):
        self.original_init_client = BigQueryClient._init_client
        BigQueryClient._init_client = Mock(return_value=True)

    def teardown_method(self):
        BigQueryClient._init_client = self.original_init_client

    def test_prepare_data(self):
        geom_column = 'the_geom'
        df = pd.DataFrame([[1, 'POINT (1 1)']], columns=['cartodb_id', geom_column])
        ds = Dataset(df)
        enrichment_service = EnrichmentService()
        expected_df = pd.DataFrame([[1, '{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                                   columns=['cartodb_id', geom_column, 'enrichment_id'])

        result = enrichment_service._prepare_data_prepare_data(ds, geom_column)
        assert result.equals(expected_df) is True
        result = enrichment_service._prepare_data(df, geom_column)
        assert result.equals(expected_df) is True

    def test_upload_dataframe(self):
        expected_project = 'carto-do-customers'
        credentials = True
        user_dataset = 'test_dataset'
        geom_column = 'the_geom'
        data_copy = pd.DataFrame([[1, '{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                                 columns=['cartodb_id', geom_column, 'enrichment_id'])
        expected_schema = {'enrichment_id': 'INTEGER', 'the_geom': 'GEOGRAPHY'}
        expected_data_copy = pd.DataFrame([['{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                                          columns=[geom_column, 'enrichment_id'])

        # mock
        def assert_upload_dataframe(_, dataframe, schema, tablename, project, dataset):
            assert dataframe.equals(expected_data_copy)
            assert schema == expected_schema
            assert isinstance(tablename, str) and len(tablename) > 0
            assert project == expected_project
            assert dataset == user_dataset

        enrichment_service = EnrichmentService()
        original = BigQueryClient.upload_dataframe
        BigQueryClient.upload_dataframe = assert_upload_dataframe

        bq_client = _get_bigquery_client(expected_project, credentials)
        enrichment_service._upload_dataframe(bq_client, user_dataset, data_copy, geom_column)

        BigQueryClient.upload_dataframe = original

    def test_execute_enrichment(self):
        expected_project = 'carto-do-customers'
        credentials = True
        geom_column = 'the_geom'
        bq_client = _get_bigquery_client(expected_project, credentials)

        df = pd.DataFrame([['{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                          columns=[geom_column, 'enrichment_id'])
        df_final = pd.DataFrame([[Point(1, 1), 'new data']], columns=[geom_column, 'var1'])

        class EnrichMock():
            def to_dataframe(self):
                return pd.DataFrame([[0, 'new data']], columns=['enrichment_id', 'var1'])

        original = BigQueryClient.query
        BigQueryClient.query = Mock(return_value=EnrichMock())
        enrichment_service = EnrichmentService()

        result = enrichment_service._execute_enrichment(bq_client, ['fake_query'], df, geom_column)

        assert result.equals(df_final)

        BigQueryClient._init_client = original
