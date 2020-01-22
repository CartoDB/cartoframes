import unittest
import pandas
import geopandas
from shapely import wkt
import uuid

from cartoframes.data.services import BQUserDataset


EXPECTED_CSV_SAMPLE = """state_fips_code,county_fips_code,geo_id,tract_name,internal_point_geo
60,10,60010950100,9501.0,POINT (-170.5618796 -14.2587411)
60,10,60010950200,9502.0,POINT (-170.5589852 -14.2859572)
60,10,60010950300,9503.0,POINT (-170.6310985 -14.2760947)
60,10,60010950500,9505.0,POINT (-170.6651925 -14.2713653)
60,10,60010950600,9506.0,POINT (-170.701028 -14.252446)
"""

class TestBQDataset(unittest.TestCase):

    def test_can_upload_from_dataframe(self):
        df = pandas.read_csv(EXPECTED_CSV_SAMPLE)
        unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
        BQUserDataset.name(unique_table_name).upload(df)

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
