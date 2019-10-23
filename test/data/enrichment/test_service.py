import unittest
import pandas as pd
from shapely.geometry.point import Point

from cartoframes.data.enrichment.enrichment_service import _prepare_data, _upload_dataframe, _enrichment_queries, \
    _execute_enrichment, _get_bigquery_client
from cartoframes.data.enrichment.points_enrichment import _prepare_sql as _prepare_sql_by_points
from cartoframes.data.enrichment.polygons_enrichment import _prepare_sql as _prepare_sql_by_polygons
from cartoframes.data import Dataset
from cartoframes.data.clients.bigquery_client import BigQueryClient

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestEnrichmentService(unittest.TestCase):
    def setUp(self):
        self.original_init_client = BigQueryClient._init_client
        BigQueryClient._init_client = Mock(return_value=True)

    def tearDown(self):
        BigQueryClient._init_client = self.original_init_client

    def test_prepare_data(self):
        geom_column = 'the_geom'
        df = pd.DataFrame([[1, 'POINT (1 1)']], columns=['cartodb_id', geom_column])
        ds = Dataset(df)

        expected_df = pd.DataFrame([[1, '{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                                   columns=['cartodb_id', geom_column, 'enrichment_id'])

        result = _prepare_data(ds, geom_column)
        self.assertTrue(result.equals(expected_df))
        result = _prepare_data(df, geom_column)
        self.assertTrue(result.equals(expected_df))

    def test_upload_dataframe(self):
        expected_project = 'carto-do-customers'
        credentails = True
        user_dataset = 'test_dataset'
        geom_column = 'the_geom'
        data_copy = pd.DataFrame([[1, '{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                                 columns=['cartodb_id', geom_column, 'enrichment_id'])
        expected_schema = {'enrichment_id': 'INTEGER', 'the_geom': 'GEOGRAPHY'}
        expected_data_copy = pd.DataFrame([['{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                                          columns=[geom_column, 'enrichment_id'])

        # mock
        def assert_upload_dataframe(_, dataframe, schema, tablename, project, dataset):
            assert dataframe.equals(expected_data_copy)
            assert schema == expected_schema
            assert isinstance(tablename, str) and len(tablename) > 0
            assert project == expected_project
            assert dataset == user_dataset

        original = BigQueryClient.upload_dataframe
        BigQueryClient.upload_dataframe = assert_upload_dataframe

        bq_client = _get_bigquery_client(expected_project, credentails)

        _upload_dataframe(bq_client, user_dataset, data_copy, geom_column)

        BigQueryClient.upload_dataframe = original

    def test_enrichment_query_by_points_one_variable(self):
        user_dataset = 'test_dataset'
        tablename = 'test_table'
        geometry_column = 'the_geom'
        query_function = _prepare_sql_by_points
        variables = 'carto-do.ags.demographics_crimerisk_usa_blockgroup_2015_yearly_2018.CRMCYBURG'
        filters = {'a': 'b'}
        kwargs = {'data_geom_column': geometry_column, 'variables': variables, 'filters': filters}

        queries = _enrichment_queries(user_dataset, tablename, query_function, **kwargs)

        expected_queries = ['''SELECT data_table.enrichment_id,
            enrichment_table.CRMCYBURG,
            ST_Area(enrichment_geo_table.geom) AS view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018_area
        FROM `carto-do-customers.{user_dataset}\
            .view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018` enrichment_table
        JOIN `carto-do-customers.{user_dataset}\
            .view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `carto-do-customers.{user_dataset}.{tablename}` data_table
        ON ST_Within(data_table.{geometry_column}, enrichment_geo_table.geom)
        WHERE a='b';''']

        expected_queries = [query.format(user_dataset=user_dataset, tablename=tablename,
                                         geometry_column=geometry_column)
                            .replace("\n", "").replace(" ", "")
                            for query in expected_queries]

        queries = [query.replace("\n", "").replace(" ", "")
                   for query in queries]

        self.assertEqual(sorted(queries), sorted(expected_queries))

    def test_enrichment_query_by_points_two_variables(self):
        user_dataset = 'test_dataset'
        tablename = 'test_table'
        geometry_column = 'the_geom'
        query_function = _prepare_sql_by_points
        variables = ['carto-do.ags.demographics_crimerisk_usa_blockgroup_2015_yearly_2018.CRMCYBURG',
                     'carto-do.mastercard.financial_mrli_usa_blockgroup_2019_monthly_2019.ticket_size_score']
        filters = {'a': 'b'}
        kwargs = {'data_geom_column': geometry_column, 'variables': variables, 'filters': filters}

        queries = _enrichment_queries(user_dataset, tablename, query_function, **kwargs)

        expected_queries = ['''SELECT data_table.enrichment_id,
            enrichment_table.CRMCYBURG,
            ST_Area(enrichment_geo_table.geom) AS view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018_area
        FROM `carto-do-customers.{user_dataset}\
            .view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018` enrichment_table
        JOIN `carto-do-customers.{user_dataset}\
            .view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `carto-do-customers.{user_dataset}.{tablename}` data_table
        ON ST_Within(data_table.{geometry_column}, enrichment_geo_table.geom)
        WHERE a='b';''', '''
        SELECT data_table.enrichment_id,
            enrichment_table.ticket_size_score,
            ST_Area(enrichment_geo_table.geom) AS view_mastercard_financial_mrli_usa_blockgroup_2019_monthly_2019_area
        FROM `carto-do-customers.{user_dataset}\
            .view_mastercard_financial_mrli_usa_blockgroup_2019_monthly_2019` enrichment_table
        JOIN `carto-do-customers.{user_dataset}\
            .view_mastercard_geography_usa_blockgroup_2019` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `carto-do-customers.{user_dataset}.{tablename}` data_table
        ON ST_Within(data_table.{geometry_column}, enrichment_geo_table.geom)
        WHERE a='b';''']

        expected_queries = [query.format(user_dataset=user_dataset, tablename=tablename,
                                         geometry_column=geometry_column)
                            .replace("\n", "").replace(" ", "")
                            for query in expected_queries]

        queries = [query.replace("\n", "").replace(" ", "")
                   for query in queries]

        self.assertEqual(sorted(queries), sorted(expected_queries))

    def test_enrichment_query_by_polygons_one_variable(self):
        user_dataset = 'test_dataset'
        tablename = 'test_table'
        geometry_column = 'the_geom'
        query_function = _prepare_sql_by_polygons
        agg_operators = {'var1': 'AVG'}
        variables = 'carto-do.ags.demographics_crimerisk_usa_blockgroup_2015_yearly_2018.CRMCYBURG'
        filters = {'a': 'b'}
        kwargs = {'data_geom_column': geometry_column, 'variables': variables,
                  'filters': filters, 'agg_operators': agg_operators}

        queries = _enrichment_queries(user_dataset, tablename, query_function, **kwargs)

        expected_queries = ['''SELECT data_table.enrichment_id, avg(enrichment_table.CRMCYBURG *\
             (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geometry_column}))\
                  / ST_area(data_table.{geometry_column}))) as CRMCYBURG
        FROM `carto-do-customers.{user_dataset}.view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018`\
             enrichment_table
        JOIN `carto-do-customers.{user_dataset}.view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `carto-do-customers.{user_dataset}.{tablename}` data_table
        ON ST_Intersects(data_table.{geometry_column}, enrichment_geo_table.geom)
        WHERE a='b'
        group by data_table.enrichment_id;''']

        expected_queries = [query.format(user_dataset=user_dataset, tablename=tablename,
                                         geometry_column=geometry_column)
                            .replace("\n", "").replace(" ", "")
                            for query in expected_queries]

        queries = [query.replace("\n", "").replace(" ", "")
                   for query in queries]

        self.assertEqual(sorted(queries), sorted(expected_queries))

    def test_enrichment_query_by_polygons_two_variables(self):
        user_dataset = 'test_dataset'
        tablename = 'test_table'
        geometry_column = 'the_geom'
        query_function = _prepare_sql_by_polygons
        agg_operators = {'var1': 'AVG'}
        variables = ['carto-do.ags.demographics_crimerisk_usa_blockgroup_2015_yearly_2018.CRMCYBURG',
                     'carto-do.mastercard.financial_mrli_usa_blockgroup_2019_monthly_2019.ticket_size_score']
        filters = {'a': 'b'}
        kwargs = {'data_geom_column': geometry_column, 'variables': variables,
                  'filters': filters, 'agg_operators': agg_operators}

        queries = _enrichment_queries(user_dataset, tablename, query_function, **kwargs)

        expected_queries = ['''SELECT data_table.enrichment_id, avg(enrichment_table.CRMCYBURG *\
             (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geometry_column}))\
                  / ST_area(data_table.{geometry_column}))) as CRMCYBURG
        FROM `carto-do-customers.{user_dataset}.view_ags_demographics_crimerisk_usa_blockgroup_2015_yearly_2018`\
             enrichment_table
        JOIN `carto-do-customers.{user_dataset}.view_ags_geography_usa_blockgroup_2015` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `carto-do-customers.{user_dataset}.{tablename}` data_table
        ON ST_Intersects(data_table.{geometry_column}, enrichment_geo_table.geom)
        WHERE a='b'
        group by data_table.enrichment_id;''', '''
        SELECT data_table.enrichment_id, avg(enrichment_table.ticket_size_score *\
             (ST_Area(ST_Intersection(enrichment_geo_table.geom, data_table.{geometry_column}))\
                  / ST_area(data_table.{geometry_column}))) as ticket_size_score
        FROM `carto-do-customers.{user_dataset}.view_mastercard_financial_mrli_usa_blockgroup_2019_monthly_2019`\
             enrichment_table
        JOIN `carto-do-customers.{user_dataset}.view_mastercard_geography_usa_blockgroup_2019` enrichment_geo_table
        ON enrichment_table.geoid = enrichment_geo_table.geoid
        JOIN `carto-do-customers.{user_dataset}.{tablename}` data_table
        ON ST_Intersects(data_table.{geometry_column}, enrichment_geo_table.geom)
        WHERE a='b'
        group by data_table.enrichment_id;
        ''']

        expected_queries = [query.format(user_dataset=user_dataset, tablename=tablename,
                                         geometry_column=geometry_column)
                            .replace("\n", "").replace(" ", "")
                            for query in expected_queries]

        queries = [query.replace("\n", "").replace(" ", "")
                   for query in queries]

        self.assertEqual(sorted(queries), sorted(expected_queries))

    def test_execute_enrichment(self):
        expected_project = 'carto-do-customers'
        credentails = True
        geom_column = 'the_geom'
        bq_client = _get_bigquery_client(expected_project, credentails)

        df = pd.DataFrame([['{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                          columns=[geom_column, 'enrichment_id'])
        df_final = pd.DataFrame([[Point(1, 1), 'new data']], columns=[geom_column, 'var1'])

        class EnrichMock():
            def to_dataframe(self):
                return pd.DataFrame([[0, 'new data']], columns=['enrichment_id', 'var1'])

        original = BigQueryClient.query
        BigQueryClient.query = Mock(return_value=EnrichMock())

        result = _execute_enrichment(bq_client, ['fake_query'], df, geom_column)

        self.assertTrue(result.equals(df_final))

        BigQueryClient._init_client = original
