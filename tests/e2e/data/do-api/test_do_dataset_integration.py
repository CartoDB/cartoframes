import os
import json
import unittest
import pandas
import geopandas
from shapely import wkt
import uuid
from io import StringIO
from pathlib import Path
from geopandas import read_file

from carto.do_dataset import DODataset, DODatasetJob

from cartoframes.auth import Credentials
from cartoframes.data.observatory.enrichment.enrichment import GEOM_TYPE_POINTS, GEOM_TYPE_POLYGONS
from cartoframes.data.observatory.enrichment.enrichment_service import _ENRICHMENT_ID, _GEOM_COLUMN, _TTL_IN_SECONDS

EXPECTED_CSV_SAMPLE = """state_fips_code,county_fips_code,geo_id,tract_name,internal_point_geo
60,10,60010950100,9501.0,POINT (-170.5618796 -14.2587411)
60,10,60010950200,9502.0,POINT (-170.5589852 -14.2859572)
60,10,60010950300,9503.0,POINT (-170.6310985 -14.2760947)
60,10,60010950500,9505.0,POINT (-170.6651925 -14.2713653)
60,10,60010950600,9506.0,POINT (-170.701028 -14.252446)
"""

CSV_SAMPLE_REDUCED = """id,geom
1,POINT (-170.5618796 -14.2587411)
2,POINT (-170.5589852 -14.2859572)
3,POINT (-170.6310985 -14.2760947)
4,POINT (-170.6651925 -14.2713653)
5,POINT (-170.701028 -14.252446)
"""


def file_path(path):
    return '{}/{}'.format(Path(__file__).parent.absolute(), path)


class TestDODataset(unittest.TestCase):
    """This test suite needs the ENV variable USERURL pointing to a working DO API in "tests/e2e/secret.json".
    DO API must have the user/apikey mapping set to get access to the user's DO Project in GCP.
    """

    def setUp(self):
        if os.environ.get('APIKEY') and os.environ.get('USERNAME') and os.environ.get('USERURL'):
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']
            self.base_url = os.environ['USERURL']
        else:
            creds = json.loads(open('tests/e2e/secret.json').read())
            self.apikey = creds['APIKEY']
            self.username = creds['USERNAME']
            self.base_url = creds['USERURL']

        credentials = Credentials(username=self.username, api_key=self.apikey, base_url=self.base_url)
        auth_client = credentials.get_api_key_auth_client()
        self.do_dataset = DODataset(auth_client=auth_client)

    def test_can_upload_from_dataframe(self):
        sample = StringIO(CSV_SAMPLE_REDUCED)
        df = pandas.read_csv(sample)
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        self.do_dataset.name(unique_table_name).upload(df)

    def test_can_upload_from_file_object(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        file_object = StringIO(CSV_SAMPLE_REDUCED)
        self.do_dataset.name(unique_table_name).upload_file_object(file_object)

    def test_can_import_a_dataset(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        file_object = StringIO(CSV_SAMPLE_REDUCED)

        dataset = self.do_dataset.name(unique_table_name) \
            .column(name='id', type='INT64') \
            .column('geom', 'GEOMETRY') \
            .ttl_seconds(30)
        dataset.create()
        dataset.upload_file_object(file_object)
        job = dataset.import_dataset()

        self.assertIsInstance(job, DODatasetJob)

    def test_can_get_status_from_import(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        file_object = StringIO(CSV_SAMPLE_REDUCED)

        dataset = self.do_dataset.name(unique_table_name) \
            .column(name='id', type='INT64') \
            .column('geom', 'GEOMETRY') \
            .ttl_seconds(30)
        dataset.create()
        dataset.upload_file_object(file_object)
        job = dataset.import_dataset()
        status = job.status()

        self.assertIn(status, ['pending', 'running', 'cancelled', 'success', 'failure'])

    def test_can_wait_for_job_completion(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        file_object = StringIO(CSV_SAMPLE_REDUCED)

        dataset = self.do_dataset.name(unique_table_name) \
            .column(name='id', type='INT64') \
            .column('geom', 'GEOMETRY') \
            .ttl_seconds(30)
        dataset.create()
        dataset.upload_file_object(file_object)
        job = dataset.import_dataset()
        status = job.result()

        self.assertIn(status, ['success'])

    def test_can_upload_a_dataframe_and_wait_for_completion(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        sample = StringIO(CSV_SAMPLE_REDUCED)
        df = pandas.read_csv(sample)

        dataset = self.do_dataset.name(unique_table_name) \
            .column(name='id', type='INT64') \
            .column('geom', 'GEOMETRY') \
            .ttl_seconds(30)
        dataset.create()
        status = dataset.upload_dataframe(df)

        self.assertIn(status, ['success'])

    def test_can_download_to_dataframe(self):
        result = self.do_dataset.name('census_tracts_american_samoa').download_stream()
        df = pandas.read_csv(result)

        self.assertEqual(df.shape, (18, 13))

        # do some checks on the contents
        sample = pandas.DataFrame(
            df.head(),
            columns=(
                'state_fips_code',
                'county_fips_code',
                'geo_id',
                'tract_name',
                'internal_point_geo'
            )
        )
        sample['internal_point_geo'] = df['internal_point_geo'].apply(wkt.loads)
        geosample = geopandas.GeoDataFrame(sample, geometry='internal_point_geo')

        self.assertEqual(geosample.to_csv(index=False), EXPECTED_CSV_SAMPLE)

    def test_creation_of_dataset(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')

        dataset = self.do_dataset.name(unique_table_name) \
            .column(name='cartodb_id', type='INT64') \
            .column('the_geom', 'GEOMETRY') \
            .ttl_seconds(30)
        dataset.create()

        # do a quick check on the resulting table
        result = dataset.download_stream()
        df = pandas.read_csv(result)
        self.assertEqual(df.shape, (0, 2))
        self.assertEqual(df.to_csv(index=False), 'cartodb_id,the_geom\n')

    def test_points_enrichment_dataset(self):
        variable_slug = 'poverty_a86da569'
        variable_column_name = 'poverty'

        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        gdf = read_file(file_path('../observatory/enrichment/files/points.geojson'))
        gdf[_ENRICHMENT_ID] = range(gdf.shape[0])
        gdf[_GEOM_COLUMN] = gdf.geometry
        gdf = gdf[[_ENRICHMENT_ID, _GEOM_COLUMN]]

        dataset = self.do_dataset.name(unique_table_name) \
            .column(_ENRICHMENT_ID, 'INT64') \
            .column(_GEOM_COLUMN, 'GEOMETRY') \
            .ttl_seconds(_TTL_IN_SECONDS)
        dataset.create()
        status = dataset.upload_dataframe(gdf)
        self.assertIn(status, ['success'])

        geom_type = GEOM_TYPE_POINTS
        variables = [variable_slug]
        output_name = '{}_result'.format(unique_table_name)
        status = dataset.enrichment(geom_type=geom_type, variables=variables, output_name=output_name)

        self.assertIn(status, ['success'])

        result = self.do_dataset.name(output_name).download_stream()
        result_df = pandas.read_csv(result)

        self.assertIn(variable_column_name, result_df.columns)

    def test_polygons_enrichment_dataset(self):
        variable_slug = 'poverty_a86da569'
        variable_column_name = 'poverty'

        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        gdf = read_file(file_path('../observatory/enrichment/files/polygon.geojson'))
        gdf[_ENRICHMENT_ID] = range(gdf.shape[0])
        gdf[_GEOM_COLUMN] = gdf.geometry
        gdf = gdf[[_ENRICHMENT_ID, _GEOM_COLUMN]]

        dataset = self.do_dataset.name(unique_table_name) \
            .column(_ENRICHMENT_ID, 'INT64') \
            .column(_GEOM_COLUMN, 'GEOMETRY') \
            .ttl_seconds(_TTL_IN_SECONDS)
        dataset.create()
        status = dataset.upload_dataframe(gdf)
        self.assertIn(status, ['success'])

        geom_type = GEOM_TYPE_POLYGONS
        variables = [variable_slug]
        output_name = '{}_result'.format(unique_table_name)
        status = dataset.enrichment(geom_type=geom_type, variables=variables, output_name=output_name)

        self.assertIn(status, ['success'])

        result = self.do_dataset.name(output_name).download_stream()
        df = pandas.read_csv(result)

        self.assertIn(variable_column_name, df.columns)
