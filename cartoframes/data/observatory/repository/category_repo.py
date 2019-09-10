from cartoframes.data.observatory.repository.repo_client import RepoClient


def get_category_repo():
    return CategoryRepository()


class CategoryRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return self._to_categories(self.client.get_categories())

    def get_by_id(self, category_id):
        result = self.client.get_categories('id', category_id)

        if len(result) == 0:
            return None

        return self._to_category(result[0])

    def get_by_country(self, iso_code):
        # TODO
        pass

    @staticmethod
    def _to_category(result):
        from cartoframes.data.observatory.category import Category

        return Category({
            'id': result['id'],
            'name': result['name']
        })

    @staticmethod
    def _to_categories(results):
        from cartoframes.data.observatory.category import Categories

        return Categories([CategoryRepository._to_category(result) for result in results])
