from cartoframes.data.clients.bigquery_client import BigQueryClient
from cartoframes.data.observatory import Enrichment

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestPointsEnrichment(object):
    def setup_method(self):
        self.original_init_client = BigQueryClient._init_client
        BigQueryClient._init_client = Mock(return_value=True)

    def teardown_method(self):
        BigQueryClient._init_client = self.original_init_client

    def test_enrichment_query_by_points_one_variable(self):
        enrichment = Enrichment()
        user_dataset = 'test_dataset'
        tablename = 'test_table'
        geometry_column = 'the_geom'
        variables = 'carto-do.ags.demographics_crimerisk_usa_blockgroup_2015_yearly_2018.CRMCYBURG'
        filters = {'a': 'b'}
        kwargs = {'data_geom_column': geometry_column, 'variables': variables, 'filters': filters}

        queries = enrichment._prepare_points_enrichment_sql(user_dataset, tablename, **kwargs)
        queries = [query.replace("\n", "").replace(" ", "") for query in queries]

        expected_queries = [
            '''
            SELECT
                data_table.enrichment_id,
                enrichment_table.CRMCYBURG,
                ST_Area(enrichment_geo_table.geom)
                    AS view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018_area
            FROM `carto-do-customers.{user_dataset}\
                .view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018` enrichment_table
            JOIN `carto-do-customers.{user_dataset}\
                .view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
            ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `carto-do-customers.{user_dataset}.{tablename}` data_table
            ON ST_Within(data_table.{geometry_column}, enrichment_geo_table.geom)
            WHERE a='b';
            '''
        ]

        expected_queries = [query.format(user_dataset=user_dataset, tablename=tablename,
                                         geometry_column=geometry_column)
                            .replace("\n", "").replace(" ", "")
                            for query in expected_queries]

        assert sorted(queries) == sorted(expected_queries)

    def test_enrichment_query_by_points_two_variables(self):
        enrichment = Enrichment()
        user_dataset = 'test_dataset'
        tablename = 'test_table'
        geometry_column = 'the_geom'
        variables = ['carto-do.ags.demographics_crimerisk_usa_blockgroup_2015_yearly_2018.CRMCYBURG',
                     'carto-do.mastercard.financial_mrli_usa_blockgroup_2019_monthly_2019.ticket_size_score']
        filters = {'a': 'b'}
        kwargs = {'data_geom_column': geometry_column, 'variables': variables, 'filters': filters}

        queries = enrichment._prepare_points_enrichment_sql(user_dataset, tablename, **kwargs)
        queries = [query.replace("\n", "").replace(" ", "") for query in queries]

        expected_queries = [
            '''
            SELECT
                data_table.enrichment_id,
                enrichment_table.CRMCYBURG,
                ST_Area(enrichment_geo_table.geom)
                    AS view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018_area
            FROM `carto-do-customers.{user_dataset}\
                .view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018` enrichment_table
            JOIN `carto-do-customers.{user_dataset}\
                .view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
            ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `carto-do-customers.{user_dataset}.{tablename}` data_table
            ON ST_Within(data_table.{geometry_column}, enrichment_geo_table.geom)
            WHERE a='b';
            ''',
            '''
            SELECT data_table.enrichment_id,
                enrichment_table.ticket_size_score,
                ST_Area(enrichment_geo_table.geom)
                    AS view_mastercard_financial_mrli_usa_blockgroup_2019_monthly_2019_area
            FROM `carto-do-customers.{user_dataset}\
                .view_mastercard_financial_mrli_usa_blockgroup_2019_monthly_2019` enrichment_table
            JOIN `carto-do-customers.{user_dataset}\
                .view_mastercard_geography_usa_blockgroup_2019` enrichment_geo_table
            ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `carto-do-customers.{user_dataset}.{tablename}` data_table
            ON ST_Within(data_table.{geometry_column}, enrichment_geo_table.geom)
            WHERE a='b';
            '''
        ]

        expected_queries = [query.format(user_dataset=user_dataset, tablename=tablename,
                                         geometry_column=geometry_column)
                            .replace("\n", "").replace(" ", "")
                            for query in expected_queries]

        assert sorted(queries) == sorted(expected_queries)
