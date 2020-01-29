import unittest
import pandas
import geopandas
from shapely import wkt
import uuid

from cartoframes.data.services import BQUserDataset, BQJob
from io import StringIO


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


class TestBQUserDataset(unittest.TestCase):

    def test_can_upload_from_dataframe(self):
        sample = StringIO(CSV_SAMPLE_REDUCED)
        df = pandas.read_csv(sample)
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        BQUserDataset.name(unique_table_name).upload(df)

    def test_can_upload_from_file_object(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        file_object = StringIO(CSV_SAMPLE_REDUCED)
        BQUserDataset.name(unique_table_name).upload_file_object(file_object)

    def test_can_import_a_dataset(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        file_object = StringIO(CSV_SAMPLE_REDUCED)

        dataset = BQUserDataset \
            .name(unique_table_name) \
            .column(name='id', type='INT64') \
            .column('geom', 'GEOMETRY') \
            .ttl_seconds(30)
        dataset.create()
        dataset.upload_file_object(file_object)
        job = dataset.import_dataset()

        self.assertIsInstance(job, BQJob)

    def test_can_get_status_from_import(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        file_object = StringIO(CSV_SAMPLE_REDUCED)

        dataset = BQUserDataset \
            .name(unique_table_name) \
            .column(name='id', type='INT64') \
            .column('geom', 'GEOMETRY') \
            .ttl_seconds(30)
        dataset.create()
        dataset.upload_file_object(file_object)
        job = dataset.import_dataset()
        status = job.status()

        self.assertIn(status, ['done', 'running', 'waiting', 'failed'])

    def test_can_wait_for_job_completion(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        file_object = StringIO(CSV_SAMPLE_REDUCED)

        dataset = BQUserDataset \
            .name(unique_table_name) \
            .column(name='id', type='INT64') \
            .column('geom', 'GEOMETRY') \
            .ttl_seconds(30)
        dataset.create()
        dataset.upload_file_object(file_object)
        job = dataset.import_dataset()
        status = job.result()

        self.assertIn(status, ['done'])

    def test_can_upload_a_dataframe_and_wait_for_completion(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        sample = StringIO(CSV_SAMPLE_REDUCED)
        df = pandas.read_csv(sample)

        dataset = BQUserDataset \
            .name(unique_table_name) \
            .column(name='id', type='INT64') \
            .column('geom', 'GEOMETRY') \
            .ttl_seconds(30)
        dataset.create()
        status = dataset.upload_dataframe(df)

        self.assertIn(status, ['done'])

    def test_can_download_to_dataframe(self):
        result = BQUserDataset.name('census_tracts_american_samoa').download_stream()
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
        dataset = BQUserDataset.name(unique_table_name) \
                               .column(name='cartodb_id', type='INT64') \
                               .column('the_geom', 'GEOMETRY') \
                               .ttl_seconds(30)
        dataset.create()

        # do a quick check on the resulting table
        result = dataset.download_stream()
        df = pandas.read_csv(result)
        self.assertEqual(df.shape, (0, 2))
        self.assertEqual(df.to_csv(index=False), 'cartodb_id,the_geom\n')

    def test_enrichment_of_dataset(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        dataset = BQUserDataset.name(unique_table_name) \
                               .column(name='cartodb_id', type='INT64') \
                               .column('the_geom', 'GEOMETRY') \
                               .ttl_seconds(30)
        dataset.create()
        geom_type = 'points'
        variables = ['carto-do.do_provider.d1.nonfamily_households']
        output_name = '{}_result'.format(unique_table_name)
        status = dataset.enrichment(geom_type=geom_type, variables=variables, output_name=output_name)

        self.assertIn(status, ['success'])

        result = BQUserDataset.name(output_name).download_stream()
        df = pandas.read_csv(result)

        self.assertIn(variables[0], df.columns)
