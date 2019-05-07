from __future__ import absolute_import


class Source(object):
    """Data source. Parent class for CARTO VL related source types:
      - :py:class:`SQL <cartoframes.carto_vl.source.SQL>`.
      - :py:class:`Dataset <cartoframes.carto_vl.source.Dataset>`.
      - :py:class:`GeoJSON <cartoframes.carto_vl.source.GeoJSON>`.

      Args:
        - query (str, GeoDataFrame): Source query for the data.
        - bounds (dict): Viewport bounds.
    """

    def __init__(self, query, bounds=None):
        self.query = query
        self.bounds = bounds
