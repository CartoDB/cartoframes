from __future__ import absolute_import
from .source import Source
from .source_types import SourceTypes


class SQL(Source):
    """Source that uses an SQL Query

        Args:
            query (str)

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
