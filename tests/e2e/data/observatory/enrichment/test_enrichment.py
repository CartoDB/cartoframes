import os
import json
from pathlib import Path

from cartoframes import CartoDataFrame
from cartoframes.auth import Credentials
from cartoframes.data.observatory import Enrichment, Variable

def file_path(path):
    return '{}/{}'.format(Path(__file__).parent.absolute(), path)


class TestEnrichment(object):
    def setup_method(self):
        if (os.environ.get('APIKEY') and os.environ.get('USERNAME')):
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']
        else:
            creds = json.loads(open('tests/e2e/secret.json').read())
            self.apikey = creds['APIKEY']
            self.username = creds['USERNAME']

        self.credentials = Credentials(self.username, self.apikey)
        self.enrichment = Enrichment(self.credentials)

        self.points_gdf = CartoDataFrame.from_file(file_path('files/points.geojson'))
        self.polygons_gdf = CartoDataFrame.from_file(file_path('files/polygon.geojson'))

        # from carto-do-public-data.usa_acs.demographics_sociodemographics_usa_censustract_2015_5yrs_20132017
        self.public_variable1 = Variable.get('poverty_a86da569'),   # FLOAT, AVG
        self.public_variable2 = Variable.get('one_car_f7f299a7'),   # FLOAT, SUM
        self.public_variable3 = Variable.get('geoid_e99a58c1')      # STRING, NONE
        self.public_variables = [
            self.public_variable1,
            self.public_variable2,
            self.public_variable3
        ]

        # from carto-do.ags.demographics_retailpotential_usa_blockgroup_2015_yearly_2019
        self.private_variable1 = Variable.get('RSGCY7224_cb77b41d')   # INTEGER, SUM
        self.private_variable2 = Variable.get('MLTCY7224_4ba39c69')   # INTEGER, SUM
        self.private_variable3 = Variable.get('BLOCKGROUP_f1b3a750')  # STRING, NONE
        self.private_variables = [
            self.private_variable1,
            self.private_variable2,
            self.private_variable3
        ]

    def teardown_method(self):
        pass

    def test_points_and_private_data(self):
        enriched_gdf = self.enrichment.enrich_points(
            self.points_gdf,
            variables=self.public_variables
        )

        expected_gdf = CartoDataFrame.from_file(file_path('files/points-private.geojson'))

        assert enriched_gdf.sort_index(axis=1).equals(expected_gdf.sort_index(axis=1))

    def test_points_public_data_and_filters(self):
        enriched_gdf = self.enrichment.enrich_points(
            self.points_gdf,
            variables=self.private_variables
        )

        expected_gdf = CartoDataFrame.from_file(file_path('files/points-private.geojson'))

        assert enriched_gdf.sort_index(axis=1).equals(expected_gdf.sort_index(axis=1))
