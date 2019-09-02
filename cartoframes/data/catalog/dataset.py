from .repository.dataset_repo import get_dataset_repo


class Dataset(object):

    def __init__(self, metadata):
        # TODO: Confirm which properties from the DDL we should include here
        self.id = metadata.id
        self.name = metadata.name
        self.provider_id = metadata.provider_id
        self.category_id = metadata.category_id
        self.geography_id = metadata.geography_id
        self.temporal_aggregations = metadata.temporal_aggregations
        self.time_coverage = metadata.time_coverage
        self.group_id = metadata.group_id
        self.version = metadata.version

    @staticmethod
    def get(dataset_id):
        metadata = get_dataset_repo().get_by_id(dataset_id)
        return Dataset(metadata)


class Datasets(list):
    def __init__(self, items):
        super(Datasets, self).__init__(items)

    @staticmethod
    def get_all():
        return [Dataset(dataset) for dataset in get_dataset_repo().get_all()]

    @staticmethod
    def get(dataset_id):
        return Dataset.get(dataset_id)