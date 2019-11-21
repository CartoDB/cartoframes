import pandas as pd
from shapely.geometry.point import Point

from cartoframes import CartoDataFrame
from cartoframes.auth import Credentials
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

    def test_prepare_data(self, mocker):
        geom_column = 'the_geom'
        enrichment_service = EnrichmentService(credentials=self.credentials)
        df = pd.DataFrame([[1, 'POINT (1 1)']], columns=['cartodb_id', geom_column])
        expected_cdf = CartoDataFrame(
            [[Point(1, 1), 0, '{"coordinates": [1.0, 1.0], "type": "Point"}']],
            columns=['geometry', 'enrichment_id', '__geojson_geom'], index=[1])

        result = enrichment_service._prepare_data(df, geom_column)
        assert result.equals(expected_cdf)

    def test_upload_data(self):
        expected_project = 'carto-do-customers'
        user_dataset = 'test_dataset'
        input_cdf = CartoDataFrame(
            [[Point(1, 1), 0, '{"coordinates": [1.0, 1.0], "type": "Point"}']],
            columns=['geometry', 'enrichment_id', '__geojson_geom'], index=[1])

        expected_schema = {'enrichment_id': 'INTEGER', '__geojson_geom': 'GEOGRAPHY'}
        expected_cdf = CartoDataFrame(
            [[0, '{"coordinates": [1.0, 1.0], "type": "Point"}']],
            columns=['enrichment_id', '__geojson_geom'], index=[1])

        # mock
        def assert_upload_data(_, dataframe, schema, tablename, project, dataset):
            assert dataframe.equals(expected_cdf)
            assert schema == expected_schema
            assert isinstance(tablename, str) and len(tablename) > 0
            assert project == expected_project
            assert tablename == user_dataset
            assert dataset == 'username'

        enrichment_service = EnrichmentService(credentials=self.credentials)
        original = BigQueryClient.upload_dataframe
        BigQueryClient.upload_dataframe = assert_upload_data
        enrichment_service._upload_data(user_dataset, input_cdf)

        BigQueryClient.upload_dataframe = original

    def test_execute_enrichment(self):
        input_cdf = CartoDataFrame(
            [[Point(1, 1), 0, '{"coordinates": [1.0, 1.0], "type": "Point"}']],
            columns=['geometry', 'enrichment_id', '__geojson_geom'], index=[1])
        expected_cdf = CartoDataFrame(
            [[Point(1, 1), 'new data']],
            columns=['geometry', 'var1'])

        class EnrichMock():
            def to_dataframe(self):
                return pd.DataFrame([[0, 'new data']], columns=['enrichment_id', 'var1'])

        original = BigQueryClient.query
        BigQueryClient.query = Mock(return_value=EnrichMock())
        enrichment_service = EnrichmentService(credentials=self.credentials)

        result = enrichment_service._execute_enrichment(['fake_query'], input_cdf)

        assert result.equals(expected_cdf)

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
