import pytest
import pandas as pd
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon

from cartoframes import CartoDataFrame
from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient
from cartoframes.data.observatory import Variable, Dataset
from cartoframes.data.observatory.catalog.repository.entity_repo import EntityRepository
from cartoframes.data.observatory.enrichment.enrichment_service import EnrichmentService, prepare_variables
from cartoframes.exceptions import EnrichmentException
from cartoframes.utils.geom_utils import to_geojson

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
        enrichment_service = EnrichmentService(credentials=self.credentials)
        point = Point(1, 1)
        df = pd.DataFrame(
            [[1, point]],
            columns=['cartodb_id', geom_column])
        expected_cdf = CartoDataFrame(
            [[1, point, 0, to_geojson(point)]],
            columns=['cartodb_id', geom_column, 'enrichment_id', '__geojson_geom'])
        expected_cdf.set_geometry(geom_column, inplace=True)

        result = enrichment_service._prepare_data(df, geom_column)

        assert result.equals(expected_cdf)

    def test_prepare_data_polygon_with_close_vertex(self):
        geom_column = 'the_geom'
        enrichment_service = EnrichmentService(credentials=self.credentials)

        polygon = Polygon([(10, 2), (1.12345688, 1), (1.12345677, 1), (10, 2)])
        df = pd.DataFrame(
            [[1, polygon]],
            columns=['cartodb_id', geom_column])

        expected_cdf = CartoDataFrame(
            [[1, polygon, 0, to_geojson(polygon)]],
            columns=['cartodb_id', geom_column, 'enrichment_id', '__geojson_geom'])
        expected_cdf.set_geometry(geom_column, inplace=True)

        result = enrichment_service._prepare_data(df, geom_column)

        assert result.equals(expected_cdf)

    def test_upload_data(self):
        geom_column = 'the_geom'
        expected_project = 'carto-do-customers'
        user_dataset = 'test_dataset'

        point = Point(1, 1)
        input_cdf = CartoDataFrame(
            [[1, point, 0, to_geojson(point)]],
            columns=['cartodb_id', geom_column, 'enrichment_id', '__geojson_geom'])
        input_cdf.set_geometry(geom_column, inplace=True)

        expected_schema = {'enrichment_id': 'INTEGER', '__geojson_geom': 'GEOGRAPHY'}
        expected_cdf = CartoDataFrame(
            [[0, to_geojson(point)]],
            columns=['enrichment_id', '__geojson_geom'])

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

    def test_upload_data_null_geometries(self):
        geom_column = 'the_geom'
        expected_project = 'carto-do-customers'
        user_dataset = 'test_dataset'

        point = Point(1, 1)
        input_cdf = CartoDataFrame(
            [[1, point, 0], [2, None, 1]],
            columns=['cartodb_id', geom_column, 'enrichment_id']
        )
        input_cdf.set_geometry(geom_column, inplace=True)

        enrichment_service = EnrichmentService(credentials=self.credentials)
        input_cdf = enrichment_service._prepare_data(input_cdf, geom_column)

        expected_schema = {'enrichment_id': 'INTEGER', '__geojson_geom': 'GEOGRAPHY'}
        expected_cdf = CartoDataFrame(
            [[0, to_geojson(point)], [1, None]],
            columns=['enrichment_id', '__geojson_geom'])

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
        geom_column = 'the_geom'
        point = Point(1, 1)
        input_cdf = CartoDataFrame(
            [[point, 0, to_geojson(point)]],
            columns=[geom_column, 'enrichment_id', '__geojson_geom'], index=[1])
        expected_cdf = CartoDataFrame(
            [[point, 'new data']],
            columns=[geom_column, 'var1'])

        class EnrichMock():
            def to_dataframe(self):
                return pd.DataFrame([[0, 'new data']], columns=['enrichment_id', 'var1'])

        original = BigQueryClient.query
        BigQueryClient.query = Mock(return_value=EnrichMock())
        enrichment_service = EnrichmentService(credentials=self.credentials)

        result = enrichment_service._execute_enrichment(['fake_query'], input_cdf)

        assert result.equals(expected_cdf)

        BigQueryClient._init_client = original

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Variable, 'get')
    def test_prepare_variables(self, get_mock, _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

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

    @patch.object(EntityRepository, 'get_by_id')
    @patch.object(Variable, 'get')
    def test_prepare_variables_raises_if_not_available_in_bq(self, get_mock, entity_repo):
        # mock dataset
        entity_repo.return_value = Dataset({
            'id': 'id',
            'slug': 'slug',
            'name': 'name',
            'description': 'description',
            'available_in': [],
            'geography_id': 'geography'
        })

        variable = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'slug': 'slug'
        })

        get_mock.return_value = variable

        with pytest.raises(EnrichmentException) as e:
            prepare_variables(variable)

        error = """
            The Dataset or the Geography of the Variable '{}' is not ready for Enrichment.
            Please, contact us for more information.
        """.format(variable.slug)
        assert str(e.value) == error

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Variable, 'get')
    def test_prepare_variables_with_agg_method(self, get_mock, _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

        variable_id = 'project.dataset.table.variable'
        variable = Variable({
            'id': variable_id,
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'agg_method': 'SUM'
        })

        get_mock.return_value = variable

        one_variable_cases = [
            variable_id,
            variable
        ]

        for case in one_variable_cases:
            result = prepare_variables(case)

            assert result == [variable]

        for case in one_variable_cases:
            result = prepare_variables(case, only_with_agg=True)

            assert result == [variable]

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Variable, 'get')
    def test_prepare_variables_without_agg_method(self, get_mock, _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

        variable_id = 'project.dataset.table.variable'
        variable = Variable({
            'id': variable_id,
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'agg_method': None
        })

        get_mock.return_value = variable

        one_variable_cases = [
            variable_id,
            variable
        ]

        for case in one_variable_cases:
            result = prepare_variables(case)

            assert result == [variable]

        for case in one_variable_cases:
            result = prepare_variables(case, only_with_agg=True)

            assert result == []
