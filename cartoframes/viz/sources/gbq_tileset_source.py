from .base_source import BaseSource

SOURCE_TYPE = 'BQMVT'


class GBQTilesetSource(BaseSource):
    """GBQTilesetSource

    Args:
        data (dict): project, dataset, tablename, token.
        metadata (str, optional): idProperty, properties.

    """
    def __init__(self, gbq_data, gbq_metadata=None, bounds=None, zoom=None):
        if not isinstance(gbq_data, dict):
            raise ValueError('Wrong source input. Valid values are dict.')

        self.type = SOURCE_TYPE
        self.gbq_data = gbq_data
        self.gbq_metadata = gbq_metadata
        self.bounds = bounds
        self.zoom = zoom

    def get_geom_type(self):
        # TODO: detect geometry type
        return 'polygon'

    def compute_metadata(self, columns=None):
        # TODO: filter metadata by columns
        self.data = {
            'data': self.gbq_data,
            'metadata': self.gbq_metadata,
            'zoom_func': self.compute_zoom_function()
        }

    def compute_zoom_function(self):
        # TODO: customize
        return '''
            (zoom) => {{
                if (zoom >= {0}) {{
                    return {0};
                }}
                return null;
            }}
        '''.format(self.zoom)
