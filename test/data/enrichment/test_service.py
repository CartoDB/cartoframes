import unittest
import pandas as pd

from cartoframes.data.enrichment.enrichment_service import _prepare_data, _upload_dataframe, _enrichment_query, \
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
        ttl = 1
        geom_column = 'the_geom'
        data_copy = pd.DataFrame([[1, '{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                                 columns=['cartodb_id', geom_column, 'enrichment_id'])
        expected_schema = {'enrichment_id': 'INTEGER', 'the_geom': 'GEOGRAPHY'}
        expected_data_copy = pd.DataFrame([['{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                                          columns=[geom_column, 'enrichment_id'])

        # mock
        def assert_upload_dataframe(_, dataframe, schema, tablename, project, dataset, ttl_days=None):
            assert dataframe.equals(expected_data_copy)
            assert schema == expected_schema
            assert isinstance(tablename, str) and len(tablename) > 0
            assert project == expected_project
            assert dataset == user_dataset
            assert ttl_days == ttl

        original = BigQueryClient.upload_dataframe
        BigQueryClient.upload_dataframe = assert_upload_dataframe

        bq_client = _get_bigquery_client(expected_project, credentails)

        _upload_dataframe(bq_client, user_dataset, data_copy, geom_column)

        BigQueryClient.upload_dataframe = original

    def test_enrichment_query_by_points(self):
        user_dataset = 'test_dataset'
        tablename = 'test_table'
        query_function = _prepare_sql_by_points
        variables = pd.DataFrame([['table1.var1'], ['table1.var2']], columns=['id'])
        filters = {'a': 'b'}
        kwargs = {'data_geom_column': 'the_geom'}

        query = _enrichment_query(user_dataset, tablename, query_function, variables, filters, **kwargs)
        expected_query = '''
            SELECT data_table.{enrichment_id},
                {variables},
                ST_Area(enrichment_geo_table.geom) AS area,
                NULL AS population
            FROM `{working_project}.{user_dataset}.{enrichment_table}` enrichment_table
            JOIN `{working_project}.{user_dataset}.{enrichment_geo_table}` enrichment_geo_table
              ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `{working_project}.{user_dataset}.{data_table}` data_table
              ON ST_Within(data_table.{data_geom_column}, enrichment_geo_table.geom)
            {filters};
        '''.format(enrichment_id='enrichment_id', variables='var1, var2',
                   enrichment_table='table1', enrichment_geo_table='geography_',
                   user_dataset=user_dataset, working_project='carto-do-customers',
                   data_table=tablename, data_geom_column='the_geom',
                   filters="WHERE a='b'")

        self.assertEqual(set(query.split(' ')), set(expected_query.split(' ')))

    def test_enrichment_query_by_polygons(self):
        user_dataset = 'test_dataset'
        tablename = 'test_table'
        query_function = _prepare_sql_by_polygons
        variables = pd.DataFrame([['table1.var1'], ['table1.var2']], columns=['id'])
        filters = {'a': 'b'}
        kwargs = {'data_geom_column': 'the_geom'}

        query = _enrichment_query(user_dataset, tablename, query_function, variables, filters, **kwargs)
        expected_query = '''
            SELECT data_table.{enrichment_id}, {variables},
            FROM `{working_project}.{user_dataset}.{enrichment_table}` enrichment_table
            JOIN `{working_project}.{user_dataset}.{enrichment_geo_table}` enrichment_geo_table
              ON enrichment_table.geoid = enrichment_geo_table.geoid
            JOIN `{working_project}.{user_dataset}.{data_table}` data_table
              ON ST_Intersects(data_table.{data_geom_column}, enrichment_geo_table.geom)
            {filters};
        '''.format(enrichment_id='enrichment_id', variables='var1, var2',
                   enrichment_table='table1', enrichment_geo_table='geography_',
                   user_dataset=user_dataset, working_project='carto-do-customers',
                   data_table=tablename, data_geom_column='the_geom',
                   filters="WHERE a='b'")

        self.assertEqual(set(query.split(' ')), set(expected_query.split(' ')))

    def test_execute_enrichment(self):
        expected_project = 'carto-do-customers'
        credentails = True
        geom_column = 'the_geom'
        bq_client = _get_bigquery_client(expected_project, credentails)

        df = pd.DataFrame([['{"coordinates": [1.0, 1.0], "type": "Point"}', 0]],
                          columns=[geom_column, 'enrichment_id'])
        df_final = pd.DataFrame([['POINT (1 1)', 'new_data']], columns=[geom_column, 'var1'])

        class EnrichMock():
            def to_dataframe(self):
                return pd.DataFrame([[0, 'new data']], columns=['enrichment_id', 'var1'])

        original = BigQueryClient.query
        BigQueryClient.query = Mock(return_value=EnrichMock())

        result = _execute_enrichment(bq_client, 'fake_query', df, geom_column)
        self.assertTrue(result.equals(df_final))

        BigQueryClient._init_client = original
