from .query_layer import QueryLayer


class Layer(QueryLayer):
    """Layer from a table name. See :py:class:`vector.QueryLayer
    <cartoframes.contrib.vector.QueryLayer>` for docs on the style attributes.

    Example:

        Visualize data from a table. Here we're using the example CartoContext.
        To use this with your account, replace the `example_context` with your
        :py:class:`CartoContext <cartoframes.context.CartoContext>` and a table
        in the account you authenticate against.

        .. code::

            from cartoframes.examples import example_context
            from cartoframes.contrib import vector
            vector.vmap(
                [vector.Layer(
                    'nat',
                    color='ramp(globalEqIntervals($hr90, 7), sunset)',
                    stroke_width_=0),
                ],
                example_context)
    """
    def __init__(self,
                 table_name,
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
