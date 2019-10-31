from cartoframes.auth import Credentials
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
        self.username = 'username'
        self.apikey = 'apikey'
        self.credentials = Credentials(self.username, self.apikey)

    def teardown_method(self):
        self.credentials = None
        self.apikey = None
        self.username = None
        BigQueryClient._init_client = self.original_init_client

    def test_enrichment_query_by_points_one_variable(self):
        enrichment = Enrichment(credentials=self.credentials)
        username = self.username
        temp_table_name = 'test_table'
        data_geom_column = 'the_geom'
        variables = enrichment._prepare_variables(
          'carto-do.ags.demographics_crimerisk_usa_blockgroup_2015_yearly_2018.CRMCYBURG'
        )
        filters = {'a': 'b'}

        actual_queries = enrichment._prepare_points_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters)

        expected_queries = [
            '''
            SELECT
                data_table.enrichment_id,
                enrichment_table.CRMCYBURG,
                ST_Area(enrichment_geo_table.geom)
                    AS view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018_area
            FROM `carto-do-customers.{username}\
                .view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018` enrichment_table
            JOIN `carto-do-customers.{username}\
                .view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
            ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `carto-do-customers.{username}.{temp_table_name}` data_table
            ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
            WHERE enrichment_table.a='b';
            '''.format(username=username, temp_table_name=temp_table_name, data_geom_column=data_geom_column),
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    def test_enrichment_query_by_points_two_variables(self):
        enrichment = Enrichment(credentials=self.credentials)
        username = self.username
        temp_table_name = 'test_table'
        data_geom_column = 'the_geom'
        variables = enrichment._prepare_variables([
            'carto-do.ags.demographics_crimerisk_usa_blockgroup_2015_yearly_2018.CRMCYBURG',
            'carto-do.mastercard.financial_mrli_usa_blockgroup_2019_monthly_2019.ticket_size_score'
        ])
        filters = {'a': 'b'}

        actual_queries = enrichment._prepare_points_enrichment_sql(
            temp_table_name, data_geom_column, variables, filters)

        expected_queries = [
            '''
            SELECT
                data_table.enrichment_id,
                enrichment_table.CRMCYBURG,
                ST_Area(enrichment_geo_table.geom)
                    AS view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018_area
            FROM `carto-do-customers.{username}\
                .view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018` enrichment_table
            JOIN `carto-do-customers.{username}\
                .view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
            ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `carto-do-customers.{username}.{temp_table_name}` data_table
            ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
            WHERE enrichment_table.a='b';
            '''.format(username=username, temp_table_name=temp_table_name, data_geom_column=data_geom_column),
            '''
            SELECT data_table.enrichment_id,
                enrichment_table.ticket_size_score,
                ST_Area(enrichment_geo_table.geom)
                    AS view_mastercard_financial_mrli_usa_blockgroup_2019_monthly_2019_area
            FROM `carto-do-customers.{username}\
                .view_mastercard_financial_mrli_usa_blockgroup_2019_monthly_2019` enrichment_table
            JOIN `carto-do-customers.{username}\
                .view_mastercard_geography_usa_blockgroup_2019` enrichment_geo_table
            ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `carto-do-customers.{username}.{temp_table_name}` data_table
            ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
            WHERE enrichment_table.a='b';
            '''.format(username=username, temp_table_name=temp_table_name, data_geom_column=data_geom_column),
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected


def _clean_queries(queries):
    return [_clean_query(query) for query in queries]


def _clean_query(query):
    return query.replace('\n', '').replace(' ', '').lower()
