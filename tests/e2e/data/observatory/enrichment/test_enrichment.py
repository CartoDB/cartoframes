import os
import json
import numpy as np
from pathlib import Path
from geopandas import read_file

from cartoframes.auth import Credentials
from cartoframes.data.observatory import Enrichment, Variable

RELATIVE_TOLERANCE = 0.001


def file_path(path):
    return '{}/{}'.format(Path(__file__).parent.absolute(), path)


def clean_gdf(gdf, sort_column=None):
    if sort_column:
        return gdf.sort_index(axis=1).sort_values(by=sort_column).reset_index(drop=True)
    else:
        return gdf.sort_index(axis=1).reset_index(drop=True)


def assert_df_equals(enriched_gdf, expected_gdf):
    assert (enriched_gdf.columns == expected_gdf.columns).all()
    assert (enriched_gdf.count() == expected_gdf.count()).all()

    for i in expected_gdf:
        enriched_values = enriched_gdf[i].values
        expected_values = expected_gdf[i].values
        if isinstance(expected_values[0], str):
            assert enriched_values.equals(expected_values)
        elif i == 'geometry':
            assert enriched_values.equals(expected_values).all()
        elif expected_values.all() is None:
            assert enriched_values.all() is None
        else:
            assert np.isclose(
                np.nan_to_num(enriched_values),
                np.nan_to_num(expected_values),
                rtol=RELATIVE_TOLERANCE
            ).all()


public_variable1 = Variable.get('poverty_a86da569')   # FLOAT, AVG
public_variable2 = Variable.get('one_car_f7f299a7')   # FLOAT, SUM
public_variable3 = Variable.get('geoid_e99a58c1')     # STRING, NONE
private_variable1 = Variable.get('RSGCY7224_cb77b41d')   # INTEGER, SUM
private_variable2 = Variable.get('MLTCY7224_4ba39c69')   # INTEGER, SUM
private_variable3 = Variable.get('BLOCKGROUP_f1b3a750')  # STRING, NONE


class TestEnrichment(object):
    def setup_method(self):
        if (os.environ.get('APIKEY') and os.environ.get('USERNAME') and os.environ.get('USERURL')):
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']
            self.base_url = os.environ['USERURL']
        else:
            creds = json.loads(open('tests/e2e/secret.json').read())
            self.apikey = creds['APIKEY']
            self.username = creds['USERNAME']
            self.base_url = creds['USERURL']

        self.credentials = Credentials(self.username, self.apikey, self.base_url)
        self.enrichment = Enrichment(self.credentials)

        self.points_gdf = read_file(file_path('files/points.geojson'))
        self.polygons_gdf = read_file(file_path('files/polygon.geojson'))

        # from carto-do-public-data.usa_acs.demographics_sociodemographics_usa_censustract_2015_5yrs_20132017
        self.public_variable1 = public_variable1
        self.public_variable2 = public_variable2
        self.public_variable3 = public_variable3
        self.public_variables = [
            self.public_variable1,
            self.public_variable2,
            self.public_variable3
        ]

        # from carto-do.ags.demographics_retailpotential_usa_blockgroup_2015_yearly_2019
        self.private_variable1 = private_variable1
        self.private_variable2 = private_variable2
        self.private_variable3 = private_variable3
        self.private_variables = [
            self.private_variable1,
            self.private_variable2,
            self.private_variable3
        ]

    def test_points_and_private_data(self):
        enriched_gdf = self.enrichment.enrich_points(
            self.points_gdf,
            variables=self.private_variables
        )

        expected_gdf = read_file(file_path('files/points-private.geojson'))

        enriched_gdf = clean_gdf(enriched_gdf)
        expected_gdf = clean_gdf(expected_gdf)

        assert_df_equals(enriched_gdf, expected_gdf)

    def test_points_public_data_and_filters(self):
        enriched_gdf = self.enrichment.enrich_points(
            self.points_gdf,
            variables=self.public_variables,
            filters={
                self.public_variable1.id: '< 300',
                self.public_variable2.id: '> 300'
            }
        )

        expected_gdf = read_file(file_path('files/points-public-filter.geojson'))

        enriched_gdf = clean_gdf(enriched_gdf)
        expected_gdf = clean_gdf(expected_gdf)

        assert_df_equals(enriched_gdf, expected_gdf)

    def test_polygons_and_public_data(self):
        enriched_gdf = self.enrichment.enrich_polygons(
            self.polygons_gdf,
            variables=self.public_variables
        )

        expected_gdf = read_file(file_path('files/polygon-public.geojson'))

        enriched_gdf = clean_gdf(enriched_gdf)
        expected_gdf = clean_gdf(expected_gdf)

        assert_df_equals(enriched_gdf, expected_gdf)

    def test_polygons_public_data_and_agg_none(self):
        enriched_gdf = self.enrichment.enrich_polygons(
            self.polygons_gdf,
            variables=self.public_variables,
            aggregation=None,
            filters={
                self.public_variable1.id: '> 300',
                self.public_variable2.id: '< 800'
            }
        )

        expected_gdf = read_file(file_path('files/polygon-public-none.geojson'))

        enriched_gdf = clean_gdf(enriched_gdf, self.public_variable1.column_name)
        expected_gdf = clean_gdf(expected_gdf, self.public_variable1.column_name)

        assert_df_equals(enriched_gdf, expected_gdf)

    def test_polygons_private_data_and_agg_custom(self):
        enriched_gdf = self.enrichment.enrich_polygons(
            self.polygons_gdf,
            variables=[self.private_variable1, self.private_variable2],
            aggregation='AVG'
        )

        expected_gdf = read_file(file_path('files/polygon-private-avg.geojson'))

        enriched_gdf = clean_gdf(enriched_gdf)
        expected_gdf = clean_gdf(expected_gdf)

        assert_df_equals(enriched_gdf, expected_gdf)

    def test_polygons_public_data_agg_custom_and_filters(self):
        enriched_gdf = self.enrichment.enrich_polygons(
            self.polygons_gdf,
            variables=[self.public_variable1, self.public_variable2],
            aggregation='SUM',
            filters={self.public_variable1.id: '> 500'}
        )

        expected_gdf = read_file(file_path('files/polygon-public-agg-custom-filter.geojson'))

        enriched_gdf = clean_gdf(enriched_gdf)
        expected_gdf = clean_gdf(expected_gdf)

        assert_df_equals(enriched_gdf, expected_gdf)

    def test_polygons_public_data_and_agg_custom_by_var(self):
        enriched_gdf = self.enrichment.enrich_polygons(
            self.polygons_gdf,
            variables=self.public_variables,
            aggregation={
                self.public_variable1.id: 'SUM',
                self.public_variable2.id: 'COUNT',
                self.public_variable3.id: 'STRING_AGG'
            }
        )

        expected_gdf = read_file(file_path('files/polygon-public-agg-custom-by-var.geojson'))

        enriched_gdf = clean_gdf(enriched_gdf)
        expected_gdf = clean_gdf(expected_gdf)

        # geoid comes with different order in each execution
        enriched_geoids = enriched_gdf["geoid"].values[0].split(',')
        enriched_geoids.sort()
        enriched_gdf["geoid"] = None
        expected_geoids = expected_gdf["geoid"].values[0].split(',')
        expected_geoids.sort()
        expected_gdf["geoid"] = None

        assert_df_equals(enriched_gdf, expected_gdf)
        assert enriched_geoids == expected_geoids
