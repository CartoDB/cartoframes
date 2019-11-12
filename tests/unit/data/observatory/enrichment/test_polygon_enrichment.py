from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient
from cartoframes.data.observatory import Enrichment, Variable, CatalogDataset
from cartoframes.data.observatory.enrichment.enrichment_service import _PUBLIC_PROJECT, _WORKING_PROJECT

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class CatalogEntityWithGeographyMock:
    def __init__(self, geography):
        self.geography = geography


class TestPolygonEnrichment(object):
    def setup_method(self):
        self.original_init_client = BigQueryClient._init_client
        BigQueryClient._init_client = Mock(return_value=True)
        self.username = 'username'
        self.apikey = 'apikey'
        self.credentials = Credentials(self.username, self.apikey)

    def teardown_method(self):
        self.credentials = None
        BigQueryClient._init_client = self.original_init_client

    @patch.object(CatalogDataset, 'get')
    def test_enrichment_query_by_polygons_one_variable(self, dataset_get_mock):
        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        data_geom_column = 'the_geom'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable_name = 'variable1'
        column = 'column1'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'AVG'
        filters = {'a': 'b'}

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'dataset_id': 'fake_name'
        })
        variables = [
            [variable, agg]
        ]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._prepare_polygon_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters
        )

        expected_queries = [
            _get_query(agg, [column], self.username, view, geo_view, temp_table_name, data_geom_column)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch.object(CatalogDataset, 'get')
    def test_enrichment_query_by_polygons_two_variables(self, dataset_get_mock):
        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        data_geom_column = 'the_geom'
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
        filters = {'a': 'b'}

        variable1 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable1_name),
            'column_name': column1,
            'dataset_id': 'fake_name'
        })
        variable2 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable2_name),
            'column_name': column2,
            'dataset_id': 'fake_name'
        })
        variables = [
            [variable1, agg],
            [variable2, agg]
        ]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._prepare_polygon_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters
        )

        expected_queries = [
            _get_query(agg, [column1, column2], self.username, view, geo_view, temp_table_name, data_geom_column)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch.object(CatalogDataset, 'get')
    def test_enrichment_query_by_polygons_two_variables_different_tables(self, dataset_get_mock):
        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        data_geom_column = 'the_geom'
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
        filters = {'a': 'b'}

        variable1 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table1, variable1_name),
            'column_name': column1,
            'dataset_id': 'fake_name'
        })
        variable2 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table2, variable2_name),
            'column_name': column2,
            'dataset_id': 'fake_name'
        })
        variables = [
            [variable1, agg],
            [variable2, agg]
        ]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._prepare_polygon_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters
        )

        expected_queries = [
            _get_query(agg, [column1], self.username, view1, geo_view, temp_table_name, data_geom_column),
            _get_query(agg, [column2], self.username, view2, geo_view, temp_table_name, data_geom_column)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch.object(CatalogDataset, 'get')
    def test_enrichment_query_by_polygons_two_variables_different_datasets(self, dataset_get_mock):
        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        data_geom_column = 'the_geom'
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
        filters = {'a': 'b'}

        variable1 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset1, table1, variable1_name),
            'column_name': column1,
            'dataset_id': 'fake_name'
        })
        variable2 = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset2, table2, variable2_name),
            'column_name': column2,
            'dataset_id': 'fake_name'
        })
        variables = [
            [variable1, agg],
            [variable2, agg]
        ]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset1, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._prepare_polygon_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters
        )

        expected_queries = [
            _get_query(agg, [column1], self.username, view1, geo_view, temp_table_name, data_geom_column),
            _get_query(agg, [column2], self.username, view2, geo_view, temp_table_name, data_geom_column)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch.object(CatalogDataset, 'get')
    def test_enrichment_query_by_polygons_without_overwritting_variable_aggregation(self, dataset_get_mock):
        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        data_geom_column = 'the_geom'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable_name = 'variable1'
        column = 'column1'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'SUM'
        filters = {'a': 'b'}

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'dataset_id': 'fake_name',
            'agg_method': agg
        })
        variables = [variable]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._prepare_polygon_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters
        )

        expected_queries = [
            _get_query(agg, [column], self.username, view, geo_view, temp_table_name, data_geom_column)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch.object(CatalogDataset, 'get')
    def test_enrichment_query_by_polygons_usging_default_aggregation(self, dataset_get_mock):
        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        data_geom_column = 'the_geom'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable_name = 'variable1'
        column = 'column1'
        geo_table = 'geo_table'
        view = 'view_{}_{}'.format(dataset, table)
        geo_view = 'view_{}_{}'.format(dataset, geo_table)
        agg = 'array_agg'
        filters = {'a': 'b'}

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'dataset_id': 'fake_name',
            'agg_method': None
        })
        variables = [variable]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._prepare_polygon_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters
        )

        expected_queries = [
            _get_query(agg, [column], self.username, view, geo_view, temp_table_name, data_geom_column)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch.object(CatalogDataset, 'get')
    def test_enrichment_query_using_public_project(self, dataset_get_mock):
        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        data_geom_column = 'the_geom'
        project = _PUBLIC_PROJECT
        dataset = 'dataset'
        table = 'table'
        variable_name = 'variable1'
        column = 'column1'
        geo_table = 'geo_table'
        agg = 'AVG'
        filters = {'a': 'b'}

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'dataset_id': '{}.{}.{}'.format(project, dataset, table)
        })
        variables = [variable]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._prepare_polygon_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters
        )

        expected_queries = [
            _get_public_query(agg, [column], self.username, dataset, table, geo_table,
                              temp_table_name, data_geom_column)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected


def _clean_queries(queries):
    return [_clean_query(query) for query in queries]


def _clean_query(query):
    return query.replace('\n', '').replace(' ', '').lower()


def _get_query(agg, columns, username, view, geo_table, temp_table_name, data_geom_column):
    columns = ', '.join(_get_column_sql(agg, column, data_geom_column) for column in columns)

    return '''
        SELECT data_table.enrichment_id, {columns}
        FROM `{project}.{username}.{view}` enrichment_table
        JOIN `{project}.{username}.{geo_table}` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `{project}.{username}.{temp_table_name}` data_table
        ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
        WHERE enrichment_table.a='b'
        group by data_table.enrichment_id;
        '''.format(
            columns=columns,
            project=_WORKING_PROJECT,
            username=username,
            view=view,
            geo_table=geo_table,
            temp_table_name=temp_table_name,
            data_geom_column=data_geom_column)


def _get_public_query(agg, columns, username, dataset, table, geo_table, temp_table_name, data_geom_column):
    columns = ', '.join(_get_column_sql(agg, column, data_geom_column) for column in columns)

    return '''
        SELECT data_table.enrichment_id, {columns}
        FROM `{public_project}.{dataset}.{table}` enrichment_table
        JOIN `{public_project}.{dataset}.{geo_table}` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `{project}.{username}.{temp_table_name}` data_table
        ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
        WHERE enrichment_table.a='b'
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
            data_geom_column=data_geom_column)


def _get_column_sql(agg, column, data_geom_column):
    return '''
        {agg}(enrichment_table.{column} *
        (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column})) /
        ST_area(data_table.{data_geom_column}))) AS {column}
        '''.format(agg=agg, column=column, data_geom_column=data_geom_column)
