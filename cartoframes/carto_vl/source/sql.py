from __future__ import absolute_import
from .source import Source
from .source_types import SourceTypes


class SQL(Source):
    """Source that uses an SQL Query

        Args:
            query (str): Query against user database. This query must have the
                following columns included to successfully have a map rendered:
                `the_geom`, `the_geom_webmercator`, and `cartodb_id`. If columns are
                used in styling, they must be included in this query as well.

        Example:

          .. code::

              from cartoframes import carto_vl as vl
              from cartoframes import CartoContext

              context = CartoContext(
                  base_url='https://cartovl.carto.com/', 
                  api_key='default_public'
              )

              vl.Map([
                  vl.Layer(
                      vl.source.SQL('SELECT * FROM populated_places WHERE adm0name = \'Spain\'')
                  )],
                  context=context
              )
    """

    source_type = SourceTypes.Query

    def __init__(self, query):
        super(SQL, self).__init__(query)
