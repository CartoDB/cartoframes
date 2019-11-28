from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient
from cartoframes.data.observatory import Enrichment, Variable, Dataset, VariableFilter
from cartoframes.data.observatory.enrichment.enrichment_service import _GEOJSON_COLUMN

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class CatalogEntityWithGeographyMock:
    def __init__(self, geography):
        self.geography = geography


class TestPointsEnrichment(object):
    def setup_method(self):
        self.original_init_client = BigQueryClient._init_client
        BigQueryClient._init_client = Mock(return_value=True)
        self.username = 'username'
        self.apikey = 'apikey'
        self.credentials = Credentials(self.username, self.apikey)

    def teardown_method(self):
        self.credentials = None
        self.apikey = None
        self.username = None
        BigQueryClient._init_client = self.original_init_client

    @patch.object(Dataset, 'get')
    def test_enrichment_query_by_points_one_variable(self, dataset_get_mock):
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
        area_name = 'view_{}_{}_area'.format(dataset, table)

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'dataset_id': 'fake_name'
        })
        variables = [variable]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._get_points_enrichment_sql(
            temp_table_name, variables, []
        )

        expected_queries = [
            get_query([column], self.username, view, geo_view, temp_table_name, area_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch.object(Dataset, 'get')
    def test_enrichment_query_by_points_two_variables(self, dataset_get_mock):
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
        area_name = 'view_{}_{}_area'.format(dataset, table)

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
        variables = [variable1, variable2]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._get_points_enrichment_sql(
            temp_table_name, variables, []
        )

        expected_queries = [
            get_query([column1, column2], self.username, view, geo_view, temp_table_name, area_name)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch.object(Dataset, 'get')
    def test_enrichment_query_by_points_two_variables_different_tables(self, dataset_get_mock):
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
        area_name1 = 'view_{}_{}_area'.format(dataset, table1)
        area_name2 = 'view_{}_{}_area'.format(dataset, table2)

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
        variables = [variable1, variable2]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._get_points_enrichment_sql(
            temp_table_name, variables, []
        )

        expected_queries = [
            get_query([column1], self.username, view1, geo_view, temp_table_name, area_name1),
            get_query([column2], self.username, view2, geo_view, temp_table_name, area_name2)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch.object(Dataset, 'get')
    def test_enrichment_query_by_points_two_variables_different_datasets(self, dataset_get_mock):
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
        area_name1 = 'view_{}_{}_area'.format(dataset1, table1)
        area_name2 = 'view_{}_{}_area'.format(dataset2, table2)

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
        variables = [variable1, variable2]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset1, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._get_points_enrichment_sql(
            temp_table_name, variables, []
        )

        expected_queries = [
            get_query([column1], self.username, view1, geo_view, temp_table_name, area_name1),
            get_query([column2], self.username, view2, geo_view, temp_table_name, area_name2)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    @patch('cartoframes.data.observatory.enrichment.enrichment_service._is_available_in_bq')
    @patch.object(Dataset, 'get')
    def test_enrichment_query_by_points_with_filters(self, dataset_get_mock, _is_available_in_bq_mock):
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
        area_name = 'view_{}_{}_area'.format(dataset, table)

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column,
            'dataset_id': 'fake_name'
        })
        variables = [variable]

        variable_filter = VariableFilter(variable, "= 'a string'")
        filters = [variable_filter]

        catalog = CatalogEntityWithGeographyMock('{}.{}.{}'.format(project, dataset, geo_table))
        dataset_get_mock.return_value = catalog

        actual_queries = enrichment._get_points_enrichment_sql(
            temp_table_name, variables, filters
        )

        expected_queries = [
            get_query([column], self.username, view, geo_view, temp_table_name, area_name, filters)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected


def _clean_queries(queries):
    return [_clean_query(query) for query in queries]


def _clean_query(query):
    return query.replace('\n', '').replace(' ', '').lower()


def get_query(columns, username, view, geo_table, temp_table_name, area_name, filters=[]):
    columns = ', '.join(get_column_sql(column) for column in columns)

    return '''
        SELECT data_table.enrichment_id, {columns}, ST_Area(enrichment_geo_table.geom) AS {area_name}
        FROM `carto-do-customers.{username}.{view}` enrichment_table
        JOIN `carto-do-customers.{username}.{geo_table}` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `carto-do-customers.{username}.{temp_table_name}` data_table
        ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
        {where};
        '''.format(
            columns=columns,
            area_name=area_name,
            username=username,
            view=view,
            geo_table=geo_table,
            temp_table_name=temp_table_name,
            data_geom_column=_GEOJSON_COLUMN,
            where=_get_where(filters))


def get_column_sql(column):
    return '''
        enrichment_table.{column}
        '''.format(column=column)


def _get_where(filters):
    where = ''
    if filters and len(filters) > 0:
        where_clausules = ["enrichment_table.{} {}".format(f.variable.column_name, f.query)
                           for f in filters]
        where = 'WHERE {}'.format('AND '.join(where_clausules))

    return where
