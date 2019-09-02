from .repo_client import RepoClient


def get_category_repo():
    return CategoryRepository()


class CategoryRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return [self._to_category(result) for result in self.client.get_categories()]

    def get_by_id(self, category_id):
        result = self.client.get_categories('id', category_id)[0]
        return self._to_category(result)

    def get_by_country(self, iso_code):
        # TODO
        pass

    @staticmethod
    def _to_category(result):
        return {
            'id': result['id'],
            'name': result['name']
        }
