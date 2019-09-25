from cartoframes.exceptions import DiscoveryException
from .repo_client import RepoClient


def get_category_repo():
    return _REPO


class CategoryRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return self._to_categories(self.client.get_categories())

    def get_by_id(self, category_id):
        result = self.client.get_categories('id', category_id)

        if len(result) == 0:
            raise DiscoveryException('The id does not correspond with any existing category in the catalog. '
                                     'You can check the full list of available categories with Categories.get_all()')

        return self._to_category(result[0])

    @staticmethod
    def _to_category(result):
        from cartoframes.data.observatory.category import Category

        return Category(result)

    @staticmethod
    def _to_categories(results):
        if len(results) == 0:
            return None

        from cartoframes.data.observatory.category import Categories

        return Categories([CategoryRepository._to_category(result) for result in results])


_REPO = CategoryRepository()
