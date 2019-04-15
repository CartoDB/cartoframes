from __future__ import absolute_import
from .query_layer import QueryLayer


class Layer(QueryLayer):
    """Layer from a table name. See :py:class:`carto.QueryLayer
    <cartoframes.carto_vl.carto.QueryLayer>` for docs on the style attributes.

    Example:

        Visualize data from a table. You have to initialize the CartoContext
        :py:class:`CartoContext <cartoframes.context.CartoContext>` with your
        credentials and a table in the account you authenticate against.

        .. code::

            from cartoframes import carto_vl as vl
            from cartoframes import CartoContext

            context = CartoContext(
                base_url='https://cartovl.carto.com/',
                api_key='default_public'
            )

            vl.Map(
                [vl.Layer('populated_places')],
                context=context
            )
    """
    def __init__(self,
                 query,
                 style=None,
                 variables=None,
                 interactivity=None,
                 legend=None):

        self.table_source = query

        super(Layer, self).__init__(
            'SELECT * FROM {}'.format(query),
            style=style,
            variables=variables,
            interactivity=interactivity,
            legend=legend
        )
