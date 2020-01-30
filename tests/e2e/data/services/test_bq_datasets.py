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

ENRICHMENT_ID = '__enrichment_id'
GEOM_COLUMN = '__geom_column'

CSV_ENRICHMENT_POINTS_SAMPLE = """{},{}
1,POINT (-79.887 36.082835)
2,POINT (-80.4061889648438 25.5151787443985)
3,POINT (-98.5021405 40.868677)
4,POINT (-107.299463 31.820398)
5,POINT (-83.987743 44.507068)
""".format(ENRICHMENT_ID, GEOM_COLUMN)

CSV_ENRICHMENT_POLYGONS_SAMPLE = """{},{}
1,POLYGON((-90.79369349999999 40.3670515, -90.79369349999999 40.5484845, -90.56156849999999 40.5484845, -90.56156849999999 40.3670515))
2,POLYGON((-96.9603555 43.58713899999999, -96.9603555 43.762051, -96.6221105 43.762051, -96.6221105 43.58713899999999))
3,POLYGON((-98.612071 40.7853815, -98.612071 40.9595765, -98.392263 40.9595765, -98.392263 40.7853815))
4,POLYGON((-97.3415835 44.890463, -97.3415835 45.064705000000004, -97.0354245 45.064705000000004, -97.0354245 44.890463))
5,POLYGON((-90.47619175 31.087278249999997, -90.47619175 31.26260875, -90.33176725000001 31.26260875, -90.33176725000001 31.087278249999997))
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
        self.assertEqual(1, 2)

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

    def test_points_enrichment_dataset(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        sample = StringIO(CSV_ENRICHMENT_POINTS_SAMPLE)
        df = pandas.read_csv(sample)

        dataset = BQUserDataset \
            .name(unique_table_name) \
            .column(ENRICHMENT_ID, 'INT64') \
            .column(GEOM_COLUMN, 'GEOMETRY') \
            .ttl_seconds(3600)
        dataset.create()
        status = dataset.upload_dataframe(df)

        self.assertIn(status, ['success'])

        geom_type = 'points'
        variables = ['nonfamily_households']
        output_name = '{}_result'.format(unique_table_name)
        status = dataset.enrichment(geom_type=geom_type, variables=variables, output_name=output_name)

        self.assertIn(status, ['success'])

        result = BQUserDataset.name(output_name).download_stream()
        df = pandas.read_csv(result)

        self.assertIn(variables[0], df.columns)

    def test_polygons_enrichment_dataset(self):
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        sample = StringIO(CSV_ENRICHMENT_POLYGONS_SAMPLE)
        df = pandas.read_csv(sample)

        dataset = BQUserDataset \
            .name(unique_table_name) \
            .column(ENRICHMENT_ID, 'INT64') \
            .column(GEOM_COLUMN, 'GEOMETRY') \
            .ttl_seconds(3600)
        dataset.create()
        status = dataset.upload_dataframe(df)

        self.assertIn(status, ['success'])

        geom_type = 'points'
        variables = ['nonfamily_households']
        output_name = '{}_result'.format(unique_table_name)
        status = dataset.enrichment(geom_type=geom_type, variables=variables, output_name=output_name)

        self.assertIn(status, ['success'])

        result = BQUserDataset.name(output_name).download_stream()
        df = pandas.read_csv(result)

        self.assertIn(variables[0], df.columns)
