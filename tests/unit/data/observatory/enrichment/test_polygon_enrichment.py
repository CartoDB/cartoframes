from google.cloud import bigquery, storage

from cartoframes.auth import Credentials

from cartoframes.data.observatory import Enrichment, Variable, Dataset, Geography, VariableFilter
from enrichment_mock import CatalogEntityWithGeographyMock, GeographyMock

from cartoframes.data.observatory.enrichment.enrichment_service import AGGREGATION_DEFAULT, AGGREGATION_NONE, \
    prepare_variables, _GEOJSON_COLUMN

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

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


class TestPolygonEnrichment(object):
    def setup_method(self):
        self.original_bigquery_Client = bigquery.Client
        bigquery.Client = Mock(return_value=True)
        self.original_storage_Client = storage.Client
        storage.Client = Mock(return_value=True)
        self.original_get_do_credentials = Credentials.get_do_credentials
        Credentials.get_do_credentials = Mock(return_value=DoCredentials(_PUBLIC_PROJECT, _WORKING_PROJECT))
        self.username = 'username'
        self.apikey = 'apikey'
        self.credentials = Credentials(self.username, self.apikey)

    def teardown_method(self):
        bigquery.Client = self.original_bigquery_Client
        storage.Client = self.original_storage_Client
        Credentials.get_do_credentials = self.original_get_do_credentials
        self.credentials = None

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_by_polygons_one_variable(self, geography_get_mock, dataset_get_mock,
                                                       _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable_name = 'variable1'
        column = 'column1'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'AVG'

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variables = [variable]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], AGGREGATION_DEFAULT
        )

        expected_queries = [
            _get_query(agg, [column], self.username, view, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._validate_bq_operations')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_by_polygons_two_variables(self, geography_get_mock, dataset_get_mock,
                                                        _validate_bq_operations_mock):
        _validate_bq_operations_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable1_name = 'variable1'
        variable2_name = 'variable2'
        column1 = 'column1'
        column2 = 'column2'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'AVG'

        variable1 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable1_name),
            'column_name': column1,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variable2 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable2_name),
            'column_name': column2,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variables = [variable1, variable2]
        aggregation = AGGREGATION_DEFAULT
        variables = prepare_variables(variables, self.credentials, aggregation)

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], AGGREGATION_DEFAULT
        )

        expected_queries = [
            _get_query(agg, [column1, column2], self.username, view, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._validate_bq_operations')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_by_polygons_two_variables_agg_none(self, geography_get_mock, dataset_get_mock,
                                                                 _validate_bq_operations_mock):
        _validate_bq_operations_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable1_name = 'variable1'
        variable2_name = 'variable2'
        column1 = 'column1'
        column2 = 'column2'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'AVG'

        variable1 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable1_name),
            'column_name': column1,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variable2 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable2_name),
            'column_name': column2,
            'agg_method': None,
            'dataset_id': 'fake_name'
        })
        variables = [variable1, variable2]
        aggregation = AGGREGATION_DEFAULT
        variables = prepare_variables(variables, self.credentials, aggregation)

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], aggregation
        )

        expected_queries = [
            _get_query(agg, [column1], self.username, view, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._validate_bq_operations')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_by_polygons_two_vars_agg_none_custom(self, geography_get_mock, dataset_get_mock,
                                                                   _validate_bq_ops_mock):
        _validate_bq_ops_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable1_name = 'variable1'
        variable2_name = 'variable2'
        column1 = 'column1'
        column2 = 'column2'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'AVG'

        variable1 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable1_name),
            'column_name': column1,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variable2 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable2_name),
            'column_name': column2,
            'agg_method': None,
            'dataset_id': 'fake_name'
        })
        variables = [variable1, variable2]
        aggregation = agg
        variables = prepare_variables(variables, self.credentials, aggregation)

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], aggregation
        )

        expected_queries = [
            _get_query(agg, [column1, column2], self.username, view, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._validate_bq_operations')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_by_polygons_two_vars_agg_none_custom2(self, geography_get_mock, dataset_get_mock,
                                                                    _validate_bq_ops_mock):
        _validate_bq_ops_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable1_name = 'variable1'
        variable2_name = 'variable2'
        column1 = 'column1'
        column2 = 'column2'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'AVG'

        variable1 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable1_name),
            'column_name': column1,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variable2 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable2_name),
            'column_name': column2,
            'agg_method': None,
            'dataset_id': 'fake_name'
        })
        variables = [variable1, variable2]
        aggregation = {variable2.id: agg}
        variables = prepare_variables(variables, self.credentials, aggregation)

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], aggregation
        )

        expected_queries = [
            _get_query(agg, [column1, column2], self.username, view, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_polygons_2_vars_different_tables(self, geography_get_mock, dataset_get_mock,
                                                               _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset = 'dataset'
        table1 = 'table1'
        table2 = 'table2'
        variable1_name = 'variable1'
        variable2_name = 'variable2'
        column1 = 'column1'
        column2 = 'column2'
        geo_table = 'geo_table'
        view1 = 'view_{}_{}'.format(dataset, table1)
        view2 = 'view_{}_{}'.format(dataset, table2)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'AVG'

        variable1 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table1, variable1_name),
            'column_name': column1,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variable2 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table2, variable2_name),
            'column_name': column2,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variables = [variable1, variable2]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], AGGREGATION_DEFAULT
        )

        expected_queries = [
            _get_query(agg, [column1], self.username, view1, geo_view, temp_table_name),
            _get_query(agg, [column2], self.username, view2, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_polygons_2_vars_different_datasets(self, geography_get_mock, dataset_get_mock,
                                                                 _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset1 = 'dataset1'
        dataset2 = 'dataset2'
        table1 = 'table1'
        table2 = 'table2'
        variable1_name = 'variable1'
        variable2_name = 'variable2'
        column1 = 'column1'
        column2 = 'column2'
        geo_table = 'geo_table'
        view1 = 'view_{}_{}'.format(dataset1, table1)
        view2 = 'view_{}_{}'.format(dataset2, table2)
        geo_view = 'view_{}_{}'.format(dataset1, geo_table)
        agg = 'AVG'

        variable1 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset1, table1, variable1_name),
            'column_name': column1,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variable2 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset2, table2, variable2_name),
            'column_name': column2,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variables = [variable1, variable2]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset1, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], AGGREGATION_DEFAULT
        )

        expected_queries = [
            _get_query(agg, [column1], self.username, view1, geo_view, temp_table_name),
            _get_query(agg, [column2], self.username, view2, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_by_polygons_agg_empty_uses_variable_one(self, geography_get_mock, dataset_get_mock,
                                                                      _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable_name = 'variable1'
        column = 'column1'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'SUM'
        aggregation = Enrichment.AGGREGATION_DEFAULT

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'dataset_id': 'fake_name',
            'agg_method': agg
        })
        variables = [variable]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], aggregation
        )

        expected_queries = [
            _get_query(agg, [column], self.username, view, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_by_polygons_agg_as_string(self, geography_get_mock, dataset_get_mock,
                                                        _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable_name = 'variable1'
        column = 'column1'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'SUM'
        aggregation = agg

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'agg_method': 'should_not_be_used',
            'dataset_id': 'fake_name'
        })
        variables = [variable]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], aggregation
        )

        expected_queries = [
            _get_query(agg, [column], self.username, view, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_by_polygons_without_agg(self, geography_get_mock, dataset_get_mock,
                                                      _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset = 'dataset1'
        table = 'table1'
        variable_name = 'variable1'
        column = 'column1'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'agg_method': 'should_not_be_used',
            'dataset_id': 'fake_name'
        })
        variables = [variable]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], AGGREGATION_NONE
        )

        expected_queries = [
            _get_query(None, [column], self.username, view, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_by_polygons_agg_custom(self, geography_get_mock, dataset_get_mock,
                                                     _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset1 = 'dataset1'
        dataset2 = 'dataset2'
        table1 = 'table1'
        table2 = 'table2'
        variable1_name = 'variable1'
        variable2_name = 'variable2'
        column1 = 'column1'
        column2 = 'column2'
        geo_table = 'geo_table'
        view1 = 'view_{}_{}'.format(dataset1, table1)
        view2 = 'view_{}_{}'.format(dataset2, table2)
        geo_view = 'view_{}_{}'.format(dataset1, geo_table)
        agg1 = 'AVG'
        agg2 = 'SUM'

        variable1 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset1, table1, variable1_name),
            'column_name': column1,
            'agg_method': agg1,
            'dataset_id': 'fake_name'
        })
        variable2 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset2, table2, variable2_name),
            'column_name': column2,
            'agg_method': 'should_not_be_used',
            'dataset_id': 'fake_name'
        })
        variables = [variable1, variable2]
        aggregation = {variable2.id: agg2}

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset1, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], aggregation
        )

        expected_queries = [
            _get_query(agg1, [column1], self.username, view1, geo_view, temp_table_name),
            _get_query(agg2, [column2], self.username, view2, geo_view, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_by_polygons_with_filters(self, geography_get_mock, dataset_get_mock,
                                                       _is_available_in_bq_mock):
        _is_available_in_bq_mock.return_value = True

        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable_name = 'variable1'
        column = 'column1'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'AVG'

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'agg_method': agg,
            'dataset_id': 'fake_name'
        })
        variables = [variable]

        variable_filter = VariableFilter(variable, "= 'a string'")
        filters = [variable_filter]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock()

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, filters, AGGREGATION_DEFAULT
        )

        expected_queries = [
            _get_query(agg, [column], self.username, view, geo_view, temp_table_name, filters)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch.object(Dataset, 'get')
    @patch.object(Geography, 'get')
    def test_enrichment_query_using_public_project(self, geography_get_mock, dataset_get_mock):
        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        project = _PUBLIC_PROJECT
        dataset = 'dataset'
        table = 'table'
        variable_name = 'variable1'
        column = 'column1'
        geo_table = 'geo_table'
        agg = 'AVG'

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'agg_method': agg,
            'dataset_id': '{}.{}.{}'.format(project, dataset, table)
        })
        variables = [variable]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog
        geography_get_mock.return_value = GeographyMock(is_public_data=True)

        actual_queries = enrichment._get_polygon_enrichment_sql(
            temp_table_name, variables, [], AGGREGATION_DEFAULT
        )

        expected_queries = [
            _get_public_query(agg, [column], self.username, dataset, table, geo_table, temp_table_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected


def _clean_queries(queries):
    return [_clean_query(query) for query in queries]


def _clean_query(query):
    return query.replace('\n', '').replace(' ', '').lower()


def _get_query(agg, columns, username, view, geo_table, temp_table_name, filters=[]):
    if agg:
        columns = ', '.join(_get_column_sql(agg, column) for column in columns)
        group = 'group by data_table.enrichment_id'
    else:
        columns = _get_column_sql_without_agg(columns)
        group = ''

    return '''
        SELECT data_table.enrichment_id, {columns}
        FROM `{project}.{username}.{view}` enrichment_table
        JOIN `{project}.{username}.{geo_table}` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `{project}.{username}.{temp_table_name}` data_table
        ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
        {where}
        {group};
        '''.format(
            columns=columns,
            project=_WORKING_PROJECT,
            username=username,
            view=view,
            geo_table=geo_table,
            temp_table_name=temp_table_name,
            data_geom_column=_GEOJSON_COLUMN,
            where=_get_where(filters),
            group=group)


def _get_column_sql(agg, column):
    agg = agg.lower()
    if (agg == 'sum'):
        return """
            {aggregation}(
                enrichment_table.{column} * (
                    ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geo_column}))
                    /
                    ST_area(data_table.{geo_column})
                )
            ) AS {aggregation}_{column}
            """.format(
                column=column,
                geo_column=_GEOJSON_COLUMN,
                aggregation=agg)
    else:
        return """
            {aggregation}(enrichment_table.{column}) AS {aggregation}_{column}
            """.format(
                column=column,
                aggregation=agg)


def _get_column_sql_without_agg(columns):
    columns = ['enrichment_table.{}'.format(column) for column in columns]

    return '''
        {columns},
        ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column})) /
        ST_area(data_table.{data_geom_column}) AS measures_proportion
        '''.format(
            columns=', '.join(columns),
            data_geom_column=_GEOJSON_COLUMN)


def _get_where(filters):
    where = ''
    if filters and len(filters) > 0:
        where_clausules = ["enrichment_table.{} {}".format(f.variable.column_name, f.query)
                           for f in filters]
        where = 'WHERE {}'.format('AND '.join(where_clausules))

    return where


def _get_public_query(agg, columns, username, dataset, table, geo_table, temp_table_name, filters=[]):
    columns = ', '.join(_get_column_sql(agg, column) for column in columns)

    return '''
        SELECT data_table.enrichment_id, {columns}
        FROM `{public_project}.{dataset}.{table}` enrichment_table
        JOIN `{public_project}.{dataset}.{geo_table}` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `{project}.{username}.{temp_table_name}` data_table
        ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
        {where}
        group by data_table.enrichment_id;
        '''.format(
            columns=columns,
            public_project=_PUBLIC_PROJECT,
            project=_WORKING_PROJECT,
            dataset=dataset,
            username=username,
            table=table,
            geo_table=geo_table,
            temp_table_name=temp_table_name,
            data_geom_column=_GEOJSON_COLUMN,
            where=_get_where(filters))
