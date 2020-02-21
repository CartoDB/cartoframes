from .base_source import BaseSource

SOURCE_TYPE = 'BQMVT'
PROJECT_KEY = 'GOOGLE_CLOUD_PROJECT'
DATAFRAME_SIZE_LIMIT = 1 * 1024


class BigQuerySource(BaseSource):
    """BigQuerySource

    Args:
        data (dict): project, dataset, tablename, token.
        metadata (str, optional): idProperty, properties.

    """
    def __init__(self, gbq_data, gbq_metadata=None):
        if not isinstance(gbq_data, dict):
            raise ValueError('Wrong source input. Valid values are dict.')

        self.type = SOURCE_TYPE
        self.gbq_data = gbq_data
        self.gbq_metadata = gbq_metadata

    def get_geom_type(self):
        return 'polygon'

    def compute_metadata(self, columns=None):
        # TODO: filter metadata by columns
        self.data = {
            'data': self.gbq_data,
            'metadata': self.gbq_metadata
        }
        self.bounds = None
