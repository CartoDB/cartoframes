from data.catalog.repo_client import RepoClient


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

    @staticmethod
    def get_datasets(self):
        return self.client.get_datasets()

    def __new__(cls):
        if Repository.__instance is None:
            Repository.instance = object.__new__(cls)
        return Repository.__instance
