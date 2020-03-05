from .base_source import BaseSource

SOURCE_TYPE = 'BQMVT'


class GBQTilesetSource(BaseSource):
    """GBQTilesetSource

    Args:
        data (dict): project, dataset, tablename, token.
        metadata (str, optional): idProperty, properties.
        bounds (list, optional)
        zooms (list, optional)

    """
    def __init__(self, gbq_data, gbq_metadata=None, bounds=None, zooms=None):
        if not isinstance(gbq_data, dict):
            raise ValueError('Wrong source input. Valid values are dict.')

        self.type = SOURCE_TYPE
        self.gbq_data = gbq_data
        self.gbq_metadata = gbq_metadata
        self.bounds = bounds
        self.zooms = zooms
        self.zoom_fn = self._compute_zoom_func()

    def get_geom_type(self):
        # TODO: detect geometry type
        return 'polygon'

    def compute_metadata(self, columns=None):
        # TODO: filter metadata by columns
        self.data = {
            'data': self.gbq_data,
            'metadata': self.gbq_metadata,
            'zoom_func': self.zoom_fn
        }

    def _compute_zoom_func(self):
        return '''
            (zoom) => {
                const zooms = %s.reverse();
                console.log(zoom, zooms)
                for (let i = 0; i < zooms.length; i++) {
                    if (zoom + 1 > zooms[i]) {
                        console.log('RETURN', zooms[i])
                        return zooms[i];
                    }
                }
                console.log('RETURN', null)
                return null;
            }
        ''' % str(self.zooms)
