from cartoframes.client import SQLClient
from cartoframes.auth import Credentials


class RepoClient(object):

    def __init__(self):
        self.client = SQLClient(Credentials('do-metadata', 'default_public'))

    def get_countries(self):
        return self.client.query('select distinct country_iso_code3 from datasets')

    def get_categories(self):
        return self.client.query('select * from categories')
