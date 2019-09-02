from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo


class Geography(object):

    def __init__(self, metadata):
        # TODO: Confirm which properties from the DDL we should include here
        self.id = metadata.id
        self.name = metadata.name
        self.provider_id = metadata.provider_id
        self.country = metadata.country
        self.version = metadata.version
        self.is_public = metadata.is_public

    @staticmethod
    def get(geography_id):
        metadata = get_geography_repo().get_by_id(geography_id)
        return Geography(metadata)

    @property
    def datasets(self):
        return get_dataset_repo().get_by_geography(self.id)


class Geographies(list):

    def __init__(self, items):
        super(Geographies, self).__init__(items)

    @staticmethod
    def get_all():
        return [Geography(var) for var in get_geography_repo().get_all()]

    @staticmethod
    def get(geography_id):
        return Geography.get(geography_id)
