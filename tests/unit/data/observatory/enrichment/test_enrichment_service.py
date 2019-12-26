import pytest
import pandas as pd

from unittest.mock import Mock, patch
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
from google.cloud import bigquery, storage

from cartoframes import CartoDataFrame
from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient
from cartoframes.data.observatory import Variable, Dataset
from cartoframes.data.observatory.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.catalog.repository.entity_repo import EntityRepository
from cartoframes.data.observatory.enrichment.enrichment_service import EnrichmentService, prepare_variables, \
    _ENRICHMENT_ID, _GEOM_COLUMN, AGGREGATION_DEFAULT, AGGREGATION_NONE, _get_aggregation, _build_where_condition, \
    _build_where_clausule, _validate_variables_input, _build_polygons_query_variables_with_aggregation, \
    _build_polygons_column_with_aggregation, _build_where_conditions_by_variable
from cartoframes.exceptions import EnrichmentException
from cartoframes.utils.geom_utils import to_geojson

_WORKING_PROJECT = 'carto-do-customers'
_PUBLIC_PROJECT = 'carto-do-public-data'


class DoCredentials:
    def __init__(self, public_data_project, user_data_project, access_token='access_token', instant_licensing=False,
                 execution_project='execution_project', dataset='username', bucket='bucket'):
        self.access_token = access_token
        self.gcp_execution_project = execution_project
        self.bq_public_project = public_data_project
        self.bq_project = user_data_project
        self.bq_dataset = dataset
        self.gcs_bucket = bucket
        self.instant_licensing = instant_licensing


class TestEnrichmentService(object):
    def setup_method(self):
        self.original_bigquery_Client = bigquery.Client
        bigquery.Client = Mock(return_value=True)
        self.original_storage_Client = storage.Client
        storage.Client = Mock(return_value=True)
        self.original_get_do_credentials = Credentials.get_do_credentials
        Credentials.get_do_credentials = Mock(return_value=DoCredentials(_PUBLIC_PROJECT, _WORKING_PROJECT))
        self.credentials = Credentials('username', 'apikey')

    def teardown_method(self):
        bigquery.Client = self.original_bigquery_Client
        storage.Client = self.original_storage_Client
        Credentials.get_do_credentials = self.original_get_do_credentials
        self.credentials = None

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
            columns=['cartodb_id', geom_column, _ENRICHMENT_ID, _GEOM_COLUMN],
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
            columns=['cartodb_id', geom_column, _ENRICHMENT_ID, _GEOM_COLUMN],
            geometry=geom_column
        )

        result = enrichment_service._prepare_data(df, geom_column)

        assert result.equals(expected_cdf)

    def test_upload_data(self):
        geom_column = 'the_geom'
        user_dataset = 'test_dataset'

        point = Point(1, 1)
        input_cdf = CartoDataFrame(
            [[1, point, 0, to_geojson(point)]],
            columns=['cartodb_id', geom_column, _ENRICHMENT_ID, _GEOM_COLUMN],
            geometry=geom_column
        )

        expected_schema = {_ENRICHMENT_ID: 'INTEGER', _GEOM_COLUMN: 'GEOGRAPHY'}
        expected_cdf = CartoDataFrame(
            [[0, to_geojson(point)]],
            columns=[_ENRICHMENT_ID, _GEOM_COLUMN])

        # mock
        def assert_upload_data(_, dataframe, schema, tablename):
            assert dataframe.equals(expected_cdf)
            assert schema == expected_schema
            assert isinstance(tablename, str) and len(tablename) > 0
            assert tablename == user_dataset

        enrichment_service = EnrichmentService(credentials=self.credentials)
        original = BigQueryClient.upload_dataframe
        BigQueryClient.upload_dataframe = assert_upload_data
        enrichment_service._upload_data(user_dataset, input_cdf)

        BigQueryClient.upload_dataframe = original

    def test_upload_data_null_geometries(self):
        geom_column = 'the_geom'
        user_dataset = 'test_dataset'

        point = Point(1, 1)
        input_cdf = CartoDataFrame(
            [[1, point, 0], [2, None, 1]],
            columns=['cartodb_id', geom_column, _ENRICHMENT_ID],
            geometry=geom_column
        )

        enrichment_service = EnrichmentService(credentials=self.credentials)
        input_cdf = enrichment_service._prepare_data(input_cdf, geom_column)

        expected_schema = {_ENRICHMENT_ID: 'INTEGER', _GEOM_COLUMN: 'GEOGRAPHY'}
        expected_cdf = CartoDataFrame(
            [[0, to_geojson(point)], [1, None]],
            columns=[_ENRICHMENT_ID, _GEOM_COLUMN])

        # mock
        def assert_upload_data(_, dataframe, schema, tablename):
            assert dataframe.equals(expected_cdf)
            assert schema == expected_schema
            assert isinstance(tablename, str) and len(tablename) > 0
            assert tablename == user_dataset

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
            columns=[geom_column, _ENRICHMENT_ID, _GEOM_COLUMN])
        expected_cdf = CartoDataFrame(
            [[point, 'new data']],
            columns=[geom_column, 'var1'])

        class JobMock():
            def __init__(self):
                self.job_id = 'job_id'
                self.errors = None

            def to_dataframe(self):
                return pd.DataFrame([[0, 'new data']], columns=[_ENRICHMENT_ID, 'var1'])

            def add_done_callback(self, callback):
                return callback(self)

        original = BigQueryClient.query
        BigQueryClient.query = Mock(return_value=JobMock())
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
        """.format(dataset.id)
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
        custom_agg = {variable_agg.id: ['sum', 'avg']}
        assert _get_aggregation(variable_agg, custom_agg) == ['sum', 'avg']
        custom_agg = {variable_agg.id: ['SUM', 'aVg']}
        assert _get_aggregation(variable_agg, custom_agg) == ['sum', 'avg']

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
        custom_agg = {variable_agg.id: ['sum', 'avg']}
        assert _get_aggregation(variable_agg_none, custom_agg) == ['sum', 'avg']
        custom_agg = {variable_agg.id: ['suM', 'AVG']}
        assert _get_aggregation(variable_agg_none, custom_agg) == ['sum', 'avg']

    def test_where_condition(self):
        column = 'column'
        condition = '> 3'

        sql = _build_where_condition(column, condition)
        expected_sql = "enrichment_table.{} {}".format(column, condition)

        assert sql == expected_sql

    def test_where_clausule(self):
        column1 = 'column1'
        condition1 = '> 1'
        filter1 = _build_where_condition(column1, condition1)

        column2 = 'column2'
        condition2 = '> 2'
        filter2 = _build_where_condition(column2, condition2)

        filters = [filter1, filter2]

        sql = _build_where_clausule(filters)
        expected_sql = 'WHERE enrichment_table.{} {} AND enrichment_table.{} {}'.format(
            column1, condition1, column2, condition2)

        assert sql == expected_sql

    def test_validate_variables_input_invalid(self):
        invalid_inputs = [
            None,
            True,
            False,
            1,
            51
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises(EnrichmentException) as e:
                _validate_variables_input(invalid_input)

            error = ('variables parameter should be a Variable instance, a list or a str.')
            assert str(e.value) == error

    def test_validate_variables_input_invalid_str(self):
        invalid_inputs = [
            '',
            []
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises(EnrichmentException) as e:
                _validate_variables_input(invalid_input)

            error = ('You should add at least one variable to be used in enrichment.')
            assert str(e.value) == error

    def test_validate_variables_input_invalid_list(self):
        invalid_inputs = [
            [i for i in range(51)]
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises(EnrichmentException) as e:
                _validate_variables_input(invalid_input)

            error = ('The maximum number of variables to be used in enrichment is 50.')
            assert str(e.value) == error

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._build_polygons_column_with_aggregation')
    def test_build_polygons_query_variables_with_aggregation(self, column_query_mock):
        def get_column(variable, aggregation, sufix=False):
            return '{}_{}'.format(variable.column_name, str(sufix))

        column_query_mock.side_effect = get_column

        variable = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'agg_method': 'SUM'
        })

        expected_result = '{}_{}'.format(variable.column_name, 'False')
        assert _build_polygons_query_variables_with_aggregation([variable], AGGREGATION_DEFAULT) == expected_result

        expected_result = '{}_{}'.format(variable.column_name, 'False')
        assert _build_polygons_query_variables_with_aggregation([variable], AGGREGATION_NONE) == expected_result

        expected_result = '{}_{}'.format(variable.column_name, 'False')
        assert _build_polygons_query_variables_with_aggregation([variable], 'AVG') == expected_result

        expected_result = '{}_{}'.format(variable.column_name, 'False')
        agg = {variable.id: 'AVG'}
        assert _build_polygons_query_variables_with_aggregation([variable], agg) == expected_result

        expected_result = '{}_{}'.format(variable.column_name, 'False')
        agg = {'unexisting_id': 'AVG'}
        assert _build_polygons_query_variables_with_aggregation([variable], agg) == expected_result

        expected_result = '{}_{}, {}_{}'.format(variable.column_name, 'True', variable.column_name, 'True')
        agg = {variable.id: ['AVG', 'SUM']}
        assert _build_polygons_query_variables_with_aggregation([variable], agg) == expected_result

    def test_build_polygons_column_with_aggregation(self):
        variable = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'agg_method': 'sum'
        })

        aggregation = 'sum'
        expected_sql = """
            sum(
                enrichment_table.{column} * (
                    ST_AREA(ST_INTERSECTION(enrichment_geo_table.geom, data_table.{geo_column}))
                    /
                    ST_AREA(data_table.{geo_column})
                )
            ) AS {column_name}
            """.format(
                column=variable.column_name,
                column_name=variable.column_name,
                geo_column=_GEOM_COLUMN)
        sql = _build_polygons_column_with_aggregation(variable, aggregation)
        assert sql == expected_sql

        aggregation = 'sum'
        expected_sql = """
            sum(
                enrichment_table.{column} * (
                    ST_AREA(ST_INTERSECTION(enrichment_geo_table.geom, data_table.{geo_column}))
                    /
                    ST_AREA(data_table.{geo_column})
                )
            ) AS {column_name}
            """.format(
                column=variable.column_name,
                column_name='sum_{}'.format(variable.column_name),
                geo_column=_GEOM_COLUMN)
        sql = _build_polygons_column_with_aggregation(variable, aggregation, True)
        assert sql == expected_sql

        aggregation = 'avg'
        expected_sql = 'avg(enrichment_table.{column}) AS {column_name}'.format(
            column=variable.column_name,
            column_name=variable.column_name)

        sql = _build_polygons_column_with_aggregation(variable, aggregation)
        assert sql.strip() == expected_sql.strip()

        aggregation = 'avg'
        expected_sql = 'avg(enrichment_table.{column}) AS {column_name}'.format(
            column=variable.column_name,
            column_name='avg_{}'.format(variable.column_name))
        sql = _build_polygons_column_with_aggregation(variable, aggregation, True)
        assert sql.strip() == expected_sql.strip()

    def test_build_where_conditions_by_variable(self):
        variable = Variable({
            'id': 'id',
            'column_name': 'column',
            'dataset_id': 'fake_name',
            'agg_method': 'sum'
        })

        filters = {}
        result = _build_where_conditions_by_variable(variable, filters)
        assert result is None

        filters = {'unexistingid': ''}
        result = _build_where_conditions_by_variable(variable, filters)
        assert result is None

        filters = {variable.id: '> 50'}
        expected = ["enrichment_table.{} > 50".format(variable.column_name)]
        result = _build_where_conditions_by_variable(variable, filters)
        assert result == expected

        filters = {variable.id: ['> 50', '< 100']}
        expected = [
            "enrichment_table.{} > 50".format(variable.column_name),
            "enrichment_table.{} < 100".format(variable.column_name)
        ]
        result = _build_where_conditions_by_variable(variable, filters)
        assert result == expected
