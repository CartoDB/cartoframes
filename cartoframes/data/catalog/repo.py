from data.catalog.repo_client import RepoClient
from data.catalog.category import Category


class Repository(object):

    __instance = None

    def __init__(self):
        self.client = RepoClient()

    @staticmethod
    def get_countries(self):
        return self.client.get_countries()

    @staticmethod
    def get_categories(self):
        return self.client.get_categories()

    def __new__(cls):
        if Repository.__instance is None:
            Repository.instance = object.__new__(cls)
        return Repository.__instance
