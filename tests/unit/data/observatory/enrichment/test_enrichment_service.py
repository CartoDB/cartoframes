import pytest
import pandas as pd
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon

from cartoframes import CartoDataFrame
from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient
from cartoframes.data.observatory import Variable, Dataset
from cartoframes.data.observatory.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.catalog.repository.entity_repo import EntityRepository
from cartoframes.data.observatory.enrichment.enrichment_service import EnrichmentService, prepare_variables, \
    _ENRICHMENT_ID, _GEOJSON_COLUMN, AGGREGATION_DEFAULT, AGGREGATION_NONE, _get_aggregation
from cartoframes.exceptions import EnrichmentException
from cartoframes.utils.geom_utils import to_geojson

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestEnrichmentService(object):
    def setup_method(self):
        self.original_init_clients = BigQueryClient._init_clients
        BigQueryClient._init_clients = Mock(return_value=(True, True))
        self.credentials = Credentials('username', 'apikey')

    def teardown_method(self):
        self.credentials = None
        BigQueryClient._init_clients = self.original_init_clients

    def test_prepare_data_no_geom(self):
        geom_column = 'the_geom'
        enrichment_service = EnrichmentService(credentials=self.credentials)
        point = Point(1, 1)
        df = pd.DataFrame(
            [[1, point]],
            columns=['cartodb_id', geom_column])

        with pytest.raises(EnrichmentException) as e:
            enrichment_service._prepare_data(df, None)

        error = ('No valid geometry found. Please provide an input source with ' +
                 'a valid geometry or specify the "geom_col" param with a geometry column.')
        assert str(e.value) == error

    def test_prepare_data(self):
        geom_column = 'the_geom'
        enrichment_service = EnrichmentService(credentials=self.credentials)
        point = Point(1, 1)
        df = pd.DataFrame(
            [[1, point]],
            columns=['cartodb_id', geom_column])
        expected_cdf = CartoDataFrame(
            [[1, point, 0, to_geojson(point)]],
            columns=['cartodb_id', geom_column, _ENRICHMENT_ID, _GEOJSON_COLUMN],
            geometry=geom_column
        )

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
            columns=['cartodb_id', geom_column, _ENRICHMENT_ID, _GEOJSON_COLUMN],
            geometry=geom_column
        )

        result = enrichment_service._prepare_data(df, geom_column)

        assert result.equals(expected_cdf)

    def test_upload_data(self):
        geom_column = 'the_geom'
        expected_project = 'carto-do-customers'
        user_dataset = 'test_dataset'

        point = Point(1, 1)
        input_cdf = CartoDataFrame(
            [[1, point, 0, to_geojson(point)]],
            columns=['cartodb_id', geom_column, _ENRICHMENT_ID, _GEOJSON_COLUMN],
            geometry=geom_column
        )

        expected_schema = {_ENRICHMENT_ID: 'INTEGER', _GEOJSON_COLUMN: 'GEOGRAPHY'}
        expected_cdf = CartoDataFrame(
            [[0, to_geojson(point)]],
            columns=[_ENRICHMENT_ID, _GEOJSON_COLUMN])

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
            columns=['cartodb_id', geom_column, _ENRICHMENT_ID],
            geometry=geom_column
        )

        enrichment_service = EnrichmentService(credentials=self.credentials)
        input_cdf = enrichment_service._prepare_data(input_cdf, geom_column)

        expected_schema = {_ENRICHMENT_ID: 'INTEGER', _GEOJSON_COLUMN: 'GEOGRAPHY'}
        expected_cdf = CartoDataFrame(
            [[0, to_geojson(point)], [1, None]],
            columns=[_ENRICHMENT_ID, _GEOJSON_COLUMN])

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
            columns=[geom_column, _ENRICHMENT_ID, _GEOJSON_COLUMN])
        expected_cdf = CartoDataFrame(
            [[point, 'new data']],
            columns=[geom_column, 'var1'])

        class EnrichMock():
            def to_dataframe(self):
                return pd.DataFrame([[0, 'new data']], columns=[_ENRICHMENT_ID, 'var1'])

        original = BigQueryClient.query
        BigQueryClient.query = Mock(return_value=EnrichMock())
        enrichment_service = EnrichmentService(credentials=self.credentials)

        result = enrichment_service._execute_enrichment(['fake_query'], input_cdf)

        assert result.equals(expected_cdf)

        BigQueryClient.query = original

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._validate_bq_operations')
    @patch.object(Variable, 'get')
    def test_prepare_variables(self, get_mock, _validate_bq_operations_mock):
        _validate_bq_operations_mock.return_value = True

        variable_id = 'project.dataset.table.variable'
        variable = Variable({
            'id': variable_id,
            'column_name': 'column',
            'dataset_id': 'fake_name'
        })

        get_mock.return_value = variable

        credentials = Credentials('fake_user', '1234')

        one_variable_cases = [
            variable_id,
            variable
        ]

        for case in one_variable_cases:
            result = prepare_variables(case, credentials)

            assert result == [variable]

        several_variables_cases = [
            [variable_id, variable_id],
            [variable, variable],
            [variable, variable_id]
        ]

        for case in several_variables_cases:
            result = prepare_variables(case, credentials)

            assert result == [variable, variable]

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._validate_bq_operations')
    @patch.object(Variable, 'get')
    def test_prepare_variables_with_agg_method(self, get_mock, _validate_bq_operations_mock):
        _validate_bq_operations_mock.return_value = True

        variable_id = 'project.dataset.table.variable'
        variable = Variable({
            'id': variable_id,
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'agg_method': 'SUM'
        })

        get_mock.return_value = variable

        credentials = Credentials('fake_user', '1234')

        one_variable_cases = [
            variable_id,
            variable
        ]

        for case in one_variable_cases:
            result = prepare_variables(case, credentials)

            assert result == [variable]

        for case in one_variable_cases:
            result = prepare_variables(case, credentials, aggregation={variable.id: 'SUM'})

            assert result == [variable]

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._validate_bq_operations')
    @patch.object(Variable, 'get')
    def test_prepare_variables_without_agg_method(self, get_mock, _validate_bq_operations_mock):
        _validate_bq_operations_mock.return_value = True

        variable_id = 'project.dataset.table.variable'
        variable = Variable({
            'id': variable_id,
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'agg_method': None
        })

        get_mock.return_value = variable

        credentials = Credentials('fake_user', '1234')

        one_variable_cases = [
            variable_id,
            variable
        ]

        for case in one_variable_cases:
            result = prepare_variables(case, credentials)

            assert result == [variable]

        for case in one_variable_cases:
            result = prepare_variables(case, credentials, aggregation={})

            assert result == []

    @patch.object(EntityRepository, 'get_by_id')
    @patch.object(Variable, 'get')
    def test_prepare_variables_raises_if_not_available_in_bq_even_public(self, get_mock, entity_repo):
        dataset = Dataset({
            'id': 'id',
            'slug': 'slug',
            'name': 'name',
            'description': 'description',
            'available_in': [],
            'geography_id': 'geography',
            'is_public_data': True
        })

        # mock dataset
        entity_repo.return_value = dataset

        variable = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'slug': 'slug'
        })

        get_mock.return_value = variable

        credentials = Credentials('fake_user', '1234')

        with pytest.raises(EnrichmentException) as e:
            prepare_variables(variable, credentials)

        error = """
            The Dataset '{}' is not ready for Enrichment. Please, contact us for more information.
        """.format(dataset)
        assert str(e.value) == error

    @patch.object(DatasetRepository, 'get_all')
    @patch.object(EntityRepository, 'get_by_id')
    @patch.object(Variable, 'get')
    def test_prepare_variables_raises_if_not_available_in_bq(self, get_mock, entity_repo, get_all_mock):
        dataset = Dataset({
            'id': 'id',
            'slug': 'slug',
            'name': 'name',
            'description': 'description',
            'available_in': [],
            'geography_id': 'geography',
            'is_public_data': False
        })

        # mock dataset
        entity_repo.return_value = dataset

        # mock subscriptions
        get_all_mock.return_value = [dataset]

        variable = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'slug': 'slug'
        })

        get_mock.return_value = variable

        credentials = Credentials('fake_user', '1234')

        with pytest.raises(EnrichmentException) as e:
            prepare_variables(variable, credentials)

        error = """
            The Dataset '{}' is not ready for Enrichment. Please, contact us for more information.
        """.format(dataset)
        assert str(e.value) == error

    @patch.object(DatasetRepository, 'get_all')
    @patch.object(EntityRepository, 'get_by_id')
    @patch.object(Variable, 'get')
    def test_prepare_variables_works_with_public_dataset(self, get_mock, entity_repo, get_all_mock):
        dataset = Dataset({
            'id': 'id',
            'slug': 'slug',
            'name': 'name',
            'description': 'description',
            'available_in': ['bq'],
            'geography_id': 'geography',
            'is_public_data': True
        })

        # mock dataset
        entity_repo.return_value = dataset

        # mock subscriptions
        get_all_mock.return_value = []

        variable = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'slug': 'slug'
        })

        get_mock.return_value = variable

        credentials = Credentials('fake_user', '1234')

        result = prepare_variables(variable, credentials)
        assert result == [variable]

    @patch.object(DatasetRepository, 'get_all')
    @patch.object(EntityRepository, 'get_by_id')
    @patch.object(Variable, 'get')
    def test_prepare_variables_fails_with_private(self, get_mock, entity_repo, get_all_mock):
        dataset = Dataset({
            'id': 'id',
            'slug': 'slug',
            'name': 'name',
            'description': 'description',
            'available_in': ['bq'],
            'geography_id': 'geography',
            'is_public_data': False
        })

        # mock dataset
        entity_repo.return_value = dataset

        # mock subscriptions
        get_all_mock.return_value = []

        variable = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'slug': 'slug'
        })

        get_mock.return_value = variable

        credentials = Credentials('fake_user', '1234')

        with pytest.raises(EnrichmentException) as e:
            prepare_variables(variable, credentials)

        error = """
            You are not subscribed to the Dataset '{}' yet. Please, use the subscribe method first.
        """.format(dataset)
        assert str(e.value) == error

    @patch.object(DatasetRepository, 'get_all')
    @patch.object(EntityRepository, 'get_by_id')
    @patch.object(Variable, 'get')
    def test_prepare_variables_works_with_private_and_subscribed(self, get_mock, entity_repo, get_all_mock):
        dataset = Dataset({
            'id': 'id',
            'slug': 'slug',
            'name': 'name',
            'description': 'description',
            'available_in': ['bq'],
            'geography_id': 'geography',
            'is_public_data': False
        })

        # mock dataset
        entity_repo.return_value = dataset

        # mock subscriptions
        get_all_mock.return_value = [dataset]

        variable = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'slug': 'slug'
        })

        get_mock.return_value = variable

        credentials = Credentials('fake_user', '1234')

        result = prepare_variables(variable, credentials)
        assert result == [variable]

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._validate_bq_operations')
    @patch.object(Variable, 'get')
    def test_prepare_variables_without_agg_method_and_custom_agg(self, get_mock, _validate_bq_operations_mock):
        _validate_bq_operations_mock.return_value = True

        variable_id = 'project.dataset.table.variable'
        variable = Variable({
            'id': variable_id,
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'agg_method': None
        })

        get_mock.return_value = variable

        credentials = Credentials('fake_user', '1234')

        one_variable_cases = [
            variable_id,
            variable
        ]

        for case in one_variable_cases:
            result = prepare_variables(case, credentials)

            assert result == [variable]

        for case in one_variable_cases:
            result = prepare_variables(case, credentials, aggregation={})

            assert result == []

        for case in one_variable_cases:
            result = prepare_variables(case, credentials, aggregation={variable_id: 'SUM'})

            assert result == [variable]

    def test_get_aggregation(self):
        variable_agg = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'agg_method': 'SUM'
        })

        assert _get_aggregation(variable_agg, AGGREGATION_DEFAULT) == variable_agg.agg_method.lower()
        assert _get_aggregation(variable_agg, AGGREGATION_NONE) is None
        assert _get_aggregation(variable_agg, 'sum') == 'sum'
        assert _get_aggregation(variable_agg, 'SUM') == 'sum'
        assert _get_aggregation(variable_agg, 'avg') == 'avg'
        assert _get_aggregation(variable_agg, 'AVG') == 'avg'
        custom_agg = {variable_agg.id: 'AVG'}
        assert _get_aggregation(variable_agg, custom_agg) == 'avg'
        custom_agg = {}
        assert _get_aggregation(variable_agg, custom_agg) == variable_agg.agg_method.lower()

        variable_agg_none = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'agg_method': None
        })

        assert _get_aggregation(variable_agg_none, AGGREGATION_DEFAULT) is None
        assert _get_aggregation(variable_agg_none, AGGREGATION_NONE) is None
        assert _get_aggregation(variable_agg_none, 'sum') == 'sum'
        assert _get_aggregation(variable_agg_none, 'SUM') == 'sum'
        assert _get_aggregation(variable_agg_none, 'avg') == 'avg'
        assert _get_aggregation(variable_agg_none, 'AVG') == 'avg'
        custom_agg = {variable_agg.id: 'AVG'}
        assert _get_aggregation(variable_agg_none, custom_agg) == 'avg'
        custom_agg = {}
        assert _get_aggregation(variable_agg_none, custom_agg) is None
