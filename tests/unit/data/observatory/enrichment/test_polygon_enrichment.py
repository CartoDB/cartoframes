from cartoframes.auth import Credentials
from cartoframes.data.clients.bigquery_client import BigQueryClient
from cartoframes.data.observatory import Enrichment

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


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

    def test_enrichment_query_by_polygons_one_variable(self):
        enrichment = Enrichment(credentials=self.credentials)
        username = self.username
        tablename = 'test_table'
        data_geom_column = 'the_geom'
        agg_operators = {'var1': 'AVG'}
        variables = enrichment._prepare_variables(
          'carto-do.ags.demographics_crimerisk_usa_blockgroup_2015_yearly_2018.CRMCYBURG'
        )

        actual_queries = enrichment._prepare_polygon_enrichment_sql(
            tablename=tablename,
            data_geom_column=data_geom_column,
            variables=variables,
            filters={'a': 'b'},
            agg_operators=agg_operators
        )

        expected_queries = [
            '''
            SELECT data_table.enrichment_id, avg(enrichment_table.CRMCYBURG *\
                (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                / ST_area(data_table.{data_geom_column})))
                AS CRMCYBURG
            FROM `carto-do-customers.{username}.view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018`\
                enrichment_table
            JOIN `carto-do-customers.{username}.view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
            ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `carto-do-customers.{username}.{tablename}` data_table
            ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
            WHERE a='b'
            group by data_table.enrichment_id;
            '''.format(username=username, tablename=tablename, data_geom_column=data_geom_column)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected

    def test_enrichment_query_by_polygons_two_variables(self):
        enrichment = Enrichment(credentials=self.credentials)
        username = self.username
        tablename = 'test_table'
        data_geom_column = 'the_geom'
        agg_operators = {'var1': 'AVG'}
        variables = enrichment._prepare_variables([
            'carto-do.ags.demographics_crimerisk_usa_blockgroup_2015_yearly_2018.CRMCYBURG',
            'carto-do.mastercard.financial_mrli_usa_blockgroup_2019_monthly_2019.ticket_size_score'
        ])

        actual_queries = enrichment._prepare_polygon_enrichment_sql(
            tablename=tablename,
            data_geom_column=data_geom_column,
            variables=variables,
            filters={'a': 'b'},
            agg_operators=agg_operators
        )

        expected_queries = [
            '''
            SELECT data_table.enrichment_id, avg(enrichment_table.CRMCYBURG *\
                (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                / ST_area(data_table.{data_geom_column}))) AS CRMCYBURG
            FROM `carto-do-customers.{username}.view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018`\
                enrichment_table
            JOIN `carto-do-customers.{username}.view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
            ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `carto-do-customers.{username}.{tablename}` data_table
            ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
            WHERE a='b'
            group by data_table.enrichment_id;
            '''.format(username=username, tablename=tablename, data_geom_column=data_geom_column),
            '''
            SELECT data_table.enrichment_id, avg(enrichment_table.ticket_size_score *\
                (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{data_geom_column}))\
                / ST_area(data_table.{data_geom_column}))) AS ticket_size_score
            FROM `carto-do-customers.{username}.view_mastercard_financial_mrli_usa_blockgroup_2019_monthly_2019`\
                enrichment_table
            JOIN `carto-do-customers.{username}.view_mastercard_geography_usa_blockgroup_2019` enrichment_geo_table
            ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `carto-do-customers.{username}.{tablename}` data_table
            ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
            WHERE a='b'
            group by data_table.enrichment_id;
          '''.format(username=username, tablename=tablename, data_geom_column=data_geom_column)
        ]

        actual = sorted(_clean_queries(actual_queries))
        expected = sorted(_clean_queries(expected_queries))

        assert actual == expected


def _clean_queries(queries):
    return [_clean_query(query) for query in queries]


def _clean_query(query):
    return query.replace('\n', '').replace(' ', '').lower()
