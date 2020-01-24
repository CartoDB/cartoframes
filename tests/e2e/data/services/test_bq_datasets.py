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


class TestBQUserDataset(unittest.TestCase):

    def test_can_upload_from_dataframe(self):
        sample = StringIO(EXPECTED_CSV_SAMPLE)
        df = pandas.read_csv(sample)
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        BQUserDataset.name(unique_table_name).upload(df)

    def test_can_upload_from_file_object(self):
        file_object = StringIO(EXPECTED_CSV_SAMPLE)
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        BQUserDataset.name(unique_table_name).upload_file_object(file_object)

    # TODO: it needs the create_dataset method to be able to import a datase from GCS to BQ
    def test_can_import_a_dataset(self):
        file_object = StringIO(EXPECTED_CSV_SAMPLE)
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        BQUserDataset.name(unique_table_name).upload_file_object(file_object)
        job = BQUserDataset.name(unique_table_name).import_dataset()
        self.assertIsInstance(job, BQJob)

    # TODO: it needs the create_dataset method to be able to import a datase from GCS to BQ
    def test_can_get_status_from_import(self):
        file_object = StringIO(EXPECTED_CSV_SAMPLE)
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        BQUserDataset.name(unique_table_name).upload_file_object(file_object)
        job = BQUserDataset.name(unique_table_name).import_dataset()
        status = job.status()
        self.assertIn(status, ['done', 'running', 'waiting', 'failed'])

    # TODO: it needs the create_dataset method to be able to import a datase from GCS to BQ
    def test_can_wait_for_job_completion(self):
        file_object = StringIO(EXPECTED_CSV_SAMPLE)
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        BQUserDataset.name(unique_table_name).upload_file_object(file_object)
        job = BQUserDataset.name(unique_table_name).import_dataset()
        status = job.result()
        self.assertIn(status, ['done', 'failed'])

    def test_can_upload_a_dataframe_and_wait_for_completion(self):
        sample = StringIO(EXPECTED_CSV_SAMPLE)
        df = pandas.read_csv(sample)
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        status = BQUserDataset.name(unique_table_name).upload_dataframe(df)
        self.assertIn(status, ['done', 'failed'])

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
