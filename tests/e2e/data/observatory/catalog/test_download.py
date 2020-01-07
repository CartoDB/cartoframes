import os
import json
import pandas
from pathlib import Path

from cartoframes.auth import Credentials
from cartoframes.data.observatory import Dataset, Geography


def file_path(path):
    return '{}/{}'.format(Path(__file__).parent.absolute(), path)


public = 'carto-do-public-data.usa_acs.demographics_sociodemographics_usa_censustract_2015_5yrs_20132017'
public_dataset = Dataset.get(public)
public_geography = Geography.get(public_dataset.geography)

private = 'carto-do.ags.demographics_retailpotential_usa_blockgroup_2015_yearly_2019'
private_dataset = Dataset.get(private)
private_geography = Geography.get(private_dataset.geography)


PUBLIC_LIMIT = 2
PRIVATE_LIMIT = 1


def clean_df(df):
    return df.sort_index(axis=1).round(5).reset_index(drop=True)


class TestDownload(object):
    def setup_method(self):
        if (os.environ.get('APIKEY') and os.environ.get('USERNAME')):
            self.apikey = os.environ['APIKEY']
            self.username = os.environ['USERNAME']
        else:
            creds = json.loads(open('tests/e2e/secret.json').read())
            self.apikey = creds['APIKEY']
            self.username = creds['USERNAME']

        self.credentials = Credentials(self.username, self.apikey)

        self.tmp_file = file_path('tmp_file.csv')

    def teardown_method(self):
        if os.path.isfile(self.tmp_file):
            os.remove(self.tmp_file)

    def test_dataset_to_csv_public(self):
        public_dataset.to_csv(self.tmp_file, self.credentials, limit=PUBLIC_LIMIT)

        assert os.path.isfile(self.tmp_file)

        df = pandas.read_csv(self.tmp_file)
        expected_df = pandas.read_csv(file_path('files/public-dataset.csv'))

        assert df.equals(expected_df)

    def test_dataset_to_csv_private(self):
        private_dataset.to_csv(self.tmp_file, self.credentials, limit=PRIVATE_LIMIT)

        assert os.path.isfile(self.tmp_file)

        df = pandas.read_csv(self.tmp_file)
        expected_df = pandas.read_csv(file_path('files/private-dataset.csv'))

        assert df.equals(expected_df)

    def test_dataset_to_dataframe_public(self):
        df = public_dataset.to_dataframe(self.credentials, limit=PUBLIC_LIMIT)
        df.to_csv(self.tmp_file, index=False)

        df = pandas.read_csv(self.tmp_file)
        expected_df = pandas.read_csv(file_path('files/public-dataset.csv'))

        assert df.equals(expected_df)

    def test_dataset_to_dataframe_private(self):
        df = private_dataset.to_dataframe(self.credentials, limit=PRIVATE_LIMIT)
        df.to_csv(self.tmp_file, index=False)

        df = pandas.read_csv(self.tmp_file)
        expected_df = pandas.read_csv(file_path('files/private-dataset.csv'))

        assert df.equals(expected_df)

    def test_geography_to_csv_public(self):
        public_geography.to_csv(self.tmp_file, self.credentials, limit=PUBLIC_LIMIT)

        assert os.path.isfile(self.tmp_file)

        df = pandas.read_csv(self.tmp_file)
        expected_df = pandas.read_csv(file_path('files/public-geography.csv'))

        assert df.equals(expected_df)

    def test_geography_to_csv_private(self):
        private_geography.to_csv(self.tmp_file, self.credentials, limit=PRIVATE_LIMIT)

        assert os.path.isfile(self.tmp_file)

        df = pandas.read_csv(self.tmp_file)
        expected_df = pandas.read_csv(file_path('files/private-geography.csv'))

        assert df.equals(expected_df)

    def test_geography_to_dataframe_public(self):
        df = public_geography.to_dataframe(self.credentials, limit=PUBLIC_LIMIT)
        df.to_csv(self.tmp_file, index=False)

        df = pandas.read_csv(self.tmp_file)
        expected_df = pandas.read_csv(file_path('files/public-geography.csv'))

        assert df.equals(expected_df)

    def test_geography_to_dataframe_private(self):
        df = private_geography.to_dataframe(self.credentials, limit=PRIVATE_LIMIT)
        df.to_csv(self.tmp_file, index=False)

        df = pandas.read_csv(self.tmp_file)
        expected_df = pandas.read_csv(file_path('files/private-geography.csv'))

        assert df.equals(expected_df)
