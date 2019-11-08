from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient
from cartoframes.data.observatory import Enrichment, Variable
from cartoframes.data.observatory.enrichment.enrichment_service import EnrichmentService

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


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

    @patch.object(EnrichmentService, '_get_tables_metadata')
    def test_enrichment_query_by_polygons_one_variable(self, _get_tables_metadata_mock):
        enrichment = Enrichment(credentials=self.credentials)

        temp_table_name = 'test_table'
        data_geom_column = 'the_geom'
        project = 'project'
        dataset = 'dataset'
        table = 'table'
        variable_name = 'variable1'
        column_name = 'column1'
        geo_table = 'geo_table'
        view_name = 'view_{}_{}'.format(dataset, table)
        agg = 'AVG'
        agg_operators = {}
        agg_operators[column_name] = agg
        filters = {'a': 'b'}

        variable = Variable({
            'id': '{}.{}.{}.{}'.format(project, dataset, table, variable_name),
            'column_name': column_name
        })
        variables = [variable]

        tables_metadata = {}
        tables_metadata[view_name] = {
            'variables': [column_name],
            'dataset': 'carto-do-customers.{}.{}'.format(self.username, view_name),
            'geo_table': 'carto-do-customers.{}.{}'.format(self.username, geo_table),
            'project': 'carto-do-customers'
        }
        _get_tables_metadata_mock.return_value = tables_metadata

        actual_queries = enrichment._prepare_polygon_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters, agg_operators
        )

        expected_queries = [
            get_query(agg, column_name, self.username, view_name, geo_table, temp_table_name, data_geom_column)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    # def test_enrichment_query_by_polygons_two_variables(self):
    #     enrichment = Enrichment(credentials=self.credentials)

    #     temp_table_name = 'test_table'
    #     data_geom_column = 'the_geom'
    #     project = 'project'
    #     dataset = 'dataset'
    #     table = 'table'
    #     variable1_name = 'variable1'
    #     variable2_name = 'variable2'
    #     column1_name = 'column1'
    #     column2_name = 'column2'
    #     geo_table = 'geo_table'
    #     view_name = 'view_{}_{}'.format(dataset, table)
    #     agg = 'AVG'
    #     agg_operators = {}
    #     agg_operators[column1_name] = agg
    #     filters = {'a': 'b'}

    #     variable1 = Variable({
    #         'id': '{}.{}.{}.{}'.format(project, dataset, table, variable1_name),
    #         'column_name': column1_name
    #     })
    #     variable2 = Variable({
    #         'id': '{}.{}.{}.{}'.format(project, dataset, table, variable2_name),
    #         'column_name': column2_name
    #     })
    #     variables = [variable1, variable2]

    #     actual_queries = enrichment._prepare_polygon_enrichment_sql(
    #         temp_table_name, data_geom_column, variables, filters, agg_operators
    #     )

    #     expected_queries = [
    #         '''
    #         SELECT data_table.enrichment_id, avg(enrichment_table.CRMCYBURG *\
    #             (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
    #             / ST_area(data_table.{data_geom_column}))) AS CRMCYBURG
    #         FROM `carto-do-customers.{username}.view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018`\
    #             enrichment_table
    #         JOIN `carto-do-customers.{username}.view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
    #         ON enrichment_table.geoid = enrichment_geo_table.geoid
    #         JOIN `carto-do-customers.{username}.{temp_table_name}` data_table
    #         ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
    #         WHERE enrichment_table.a='b'
    #         group by data_table.enrichment_id;
    #         '''.format(username=username, temp_table_name=temp_table_name, data_geom_column=data_geom_column),
    #         '''
    #         SELECT data_table.enrichment_id, avg(enrichment_table.ticket_size_score *\
    #             (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
    #             / ST_area(data_table.{data_geom_column}))) AS ticket_size_score
    #         FROM `carto-do-customers.{username}.view_mastercard_financial_mrli_usa_blockgroup_2019_monthly_2019`\
    #             enrichment_table
    #         JOIN `carto-do-customers.{username}.view_mastercard_geography_usa_blockgroup_2019` enrichment_geo_table
    #         ON enrichment_table.geoid = enrichment_geo_table.geoid
    #         JOIN `carto-do-customers.{username}.{temp_table_name}` data_table
    #         ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
    #         WHERE enrichment_table.a='b'
    #         group by data_table.enrichment_id;
    #       '''.format(username=username, temp_table_name=temp_table_name, data_geom_column=data_geom_column)
    #     ]

    #     actual = sorted(_clean_queries(actual_queries))
    #     expected = sorted(_clean_queries(expected_queries))

    #     assert actual == expected


def _clean_queries(queries):
    return [_clean_query(query) for query in queries]


def _clean_query(query):
    return query.replace('\n', '').replace(' ', '').lower()


def get_query(agg, column_name, username, view_name, geo_table, temp_table_name, data_geom_column):
    return '''
        SELECT data_table.enrichment_id, {agg}(enrichment_table.{column} *\
            (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
            / ST_area(data_table.{data_geom_column})))
            AS {column}
        FROM `carto-do-customers.{username}.{view}`\
            enrichment_table
        JOIN `carto-do-customers.{username}.{geo_table}` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `carto-do-customers.{username}.{temp_table_name}` data_table
        ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
        WHERE enrichment_table.a='b'
        group by data_table.enrichment_id;
        '''.format(
            agg=agg,
            column=column_name,
            username=username,
            view=view_name,
            geo_table=geo_table,
            temp_table_name=temp_table_name,
            data_geom_column=data_geom_column)
