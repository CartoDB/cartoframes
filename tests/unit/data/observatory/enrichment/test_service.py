import pandas as pd
from shapely.geometry.point import Point

from cartoframes.auth import Credentials
from cartoframes.data import Dataset
from cartoframes.data.clients.bigquery_client import BigQueryClient
from cartoframes.data.observatory.enrichment.enrichment_service import EnrichmentService, prepare_variables
from cartoframes.data.observatory import Variable

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestEnrichmentService(object):
    def setup_method(self):
        self.original_init_client = BigQueryClient._init_client
        BigQueryClient._init_client = Mock(return_value=True)
        self.credentials = Credentials('username', 'apikey')

    def teardown_method(self):
        self.credentials = None
        BigQueryClient._init_client = self.original_init_client

    def test_prepare_data(self):
        geom_column = 'the_geom'
        df = pd.DataFrame([[1, 'POINT (1 1)']], columns=['cartodb_id', geom_column])
        ds = Dataset(df)
        enrichment_service = EnrichmentService(credentials=self.credentials)
        expected_df = pd.DataFrame([[1, '{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                                   columns=['cartodb_id', geom_column, 'enrichment_id'])

        result = enrichment_service._prepare_data(ds, geom_column)
        assert result.equals(expected_df) is True
        result = enrichment_service._prepare_data(df, geom_column)
        assert result.equals(expected_df) is True

    def test_upload_dataframe(self):
        expected_project = 'carto-do-customers'
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
            assert tablename == user_dataset
            assert dataset == 'username'

        enrichment_service = EnrichmentService(credentials=self.credentials)
        original = BigQueryClient.upload_dataframe
        BigQueryClient.upload_dataframe = assert_upload_dataframe
        enrichment_service._upload_dataframe(user_dataset, data_copy, geom_column)

        BigQueryClient.upload_dataframe = original

    def test_execute_enrichment(self):
        geom_column = 'the_geom'
        df = pd.DataFrame([['{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                          columns=[geom_column, 'enrichment_id'])
        df_final = pd.DataFrame([[Point(1, 1), 'new data']], columns=[geom_column, 'var1'])

        class EnrichMock():
            def to_dataframe(self):
                return pd.DataFrame([[0, 'new data']], columns=['enrichment_id', 'var1'])

        original = BigQueryClient.query
        BigQueryClient.query = Mock(return_value=EnrichMock())
        enrichment_service = EnrichmentService(credentials=self.credentials)

        result = enrichment_service._execute_enrichment(['fake_query'], df, geom_column)

        assert result.equals(df_final)

        BigQueryClient._init_client = original

    @patch.object(Variable, 'get')
    def test_prepare_variables(self, get_mock):
        variable_id = 'project.dataset.table.variable'
        variable = Variable({
            'id': variable_id,
            'column_name': 'column',
            'dataset_id': 'fake_name'
        })

        get_mock.return_value = variable

        one_variable_cases = [
            variable_id,
            variable
        ]

        for case in one_variable_cases:
            result = prepare_variables(case)

            assert result == [variable]

        several_variables_cases = [
            [variable_id, variable_id],
            [variable, variable],
            [variable, variable_id]
        ]

        for case in several_variables_cases:
            result = prepare_variables(case)

            assert result == [variable, variable]
