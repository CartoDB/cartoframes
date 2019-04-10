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

            from cartoframes.carto_vl import carto
            from cartoframes import CartoContext

            context = CartoContext(
                base_url='https://cartovl.carto.com/',
                api_key='default_public'
            )

            carto.Map(
                [carto.Layer('populated_places')],
                context=context
            ).init()
    """
    def __init__(self,
                 table_name,
                 viz=None,
                 color_=None,
                 width_=None,
                 filter_=None,
                 stroke_color_=None,
                 stroke_width_=None,
                 transform_=None,
                 order_=None,
                 symbol_=None,
                 variables=None,
                 legend=None,
                 interactivity=None):

        self.table_source = table_name

        super(Layer, self).__init__(
            'SELECT * FROM {}'.format(table_name),
            viz=viz,
            color_=color_,
            width_=width_,
            filter_=filter_,
            stroke_color_=stroke_color_,
            stroke_width_=stroke_width_,
            transform_=transform_,
            order_=order_,
            symbol_=symbol_,
            variables=variables,
            legend=legend,
            interactivity=interactivity
        )
