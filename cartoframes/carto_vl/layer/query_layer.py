class QueryLayer(object):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """CARTO VL layer based on an arbitrary query against user database

    Args:
        query (str): Query against user database. This query must have the
          following columns included to successfully have a map rendered:
          `the_geom`, `the_geom_webmercator`, and `cartodb_id`. If columns are
          used in styling, they must be included in this query as well.
        viz (str, optional): Instead of declaring style properties one by one,
          you can make use of CARTO VL `vizString` through this parameter.
        color_ (str, optional): CARTO VL color styling for this layer. Valid
          inputs are simple web color names and hex values. For more advanced
          styling, see the CARTO VL guide on styling for more information:
          https://carto.com/developers/carto-vl/guides/styling-points/
        width_ (float or str, optional): CARTO VL width styling for this layer if
          points or lines (which are not yet implemented). Valid inputs are
          positive numbers or text expressions involving variables. To remain
          consistent with cartoframes' raster-based :py:class:`Layer
          <cartoframes.layer.Layer>` API, `size` is used here in place of
          `width`, which is the CARTO VL variable name for controlling the
          width of a point or line. Default size is 7 pixels wide.
        filter_ (str, optional): Time expression to animate data. This is an alias
          for the CARTO VL `filter` style attribute. Default is no animation.
        stroke_color_ (str, optional): Defines the stroke color of polygons.
          Default is white.
        stroke_width_ (float or str, optional): Defines the width of the stroke
          in pixels. Default is 1.
        symbol_ (str, optional): Show an image instead in the place of points
        symbol_placement_ (str, optional): When using symbol , offset to apply to the image
        order_ (str, optional): Rendering order of the features, only applicable to points.
        transform_ (str, optional): Apply a rotation or a translation to the feature.
        resolution_ (float or str, optional): resolution of the property-aggregation functions,
          only applicable to points.
          Default resolution is 1.
          Custom values must be greater than 0 and lower than 256.
          A resolution of N means points are aggregated to grid cells NxN pixels.
          Unlinke Torque resolution, the aggregated points are placed in the centroid of
          the cluster, not in the center of the grid cell.
        variables (list, optional): When you have to define variables to be reused
        interactivity (str, list, or dict, optional): This option adds
          interactivity (click or hover) to a layer. Defaults to ``click`` if
          one of the following inputs are specified:
          - dict: If a :obj:`dict`, this must have the key `cols` with its
            value a list of columns. Optionally add `event` to choose ``hover``
            or ``click``. Specifying a `header` key/value pair adds a header to
            the popup that will be rendered in HTML.
          - list: A list of valid column names in the data used for this layer
          - str: A column name in the data used in this layer

    Example:

        .. code::

            from cartoframes.examples import example_context
            from cartoframes.carto_vl import carto
            # create geometries from lng/lat columns

            query = '''
               SELECT *, ST_Transform(the_geom, 3857) as the_geom_webmercator
               FROM (
                   SELECT
                     CDB_LatLng(pickup_latitude, pickup_longitude) as the_geom,
                     fare_amount,
                     cartodb_id
                   FROM taxi_50k
               ) as _w
            '''

            carto.Map(
                [carto.QueryLayer(query)],
                example_context,
                interactivity={
                    'cols': ['fare_amount'],
                    'event': 'hover'
                }
            )
    """

    def __init__(self,
                 query,
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
                 interactivity=None,
                 legend=None):

        def convstr(obj):
            """convert all types to strings or None"""
            return str(obj) if obj is not None else None

        # data source
        self.query = query

        # viz string
        self.viz = viz

        # style attributes
        self.color_ = color_
        self.width_ = convstr(width_)
        self.filter_ = filter_
        self.stroke_color_ = stroke_color_
        self.stroke_width_ = convstr(stroke_width_)
        self.transform_ = transform_
        self.order_ = order_
        self.symbol_ = symbol_

        # legends
        self.legend = legend

        # internal attributes
        self.orig_query = query
        self.is_basemap = False
        self.styling = ''
        self.interactivity = None
        self.header = None

        if (self.viz is None):
            self._compose_style()
            # variables
            self._set_variables(variables)
            # interactivity options
            self._set_interactivity(interactivity)
        else:
            self.styling = self.viz

    def _compose_style(self):
        """Appends `prop` with `style` to layer styling"""
        valid_styles = (
            'color',
            'width',
            'filter',
            'stroke_width',
            'stroke_color',
            'transform',
            'order',
            'symbol'
        )

        self.styling = '\n'.join(
            '{prop}: {style}'.format(
              prop=_to_camel_case(s),
              style=getattr(self, s + '_')
            ) for s in valid_styles if getattr(self, s + '_') is not None
        )

    def _set_variables(self, variables):
        if variables is None:
            self.variables = None
            return
        elif isinstance(variables, (list)):
            self.variables = variables
            variables_list = '\n'.join(
                '@{name}: {value}'.format(
                    name=variable[0],
                    value=variable[1]
                ) for variable in variables
            )
        elif isinstance(variables, dict):
            self.variables = variables
            variables_list = '\n'.join(
                '@{name}: ${value}'.format(variable)
                for variable in variables
            )
        else:
            raise ValueError('`variables` must be a list of [ name, value ]')

        self.styling = '\n'.join([variables_list, self.styling])

    def _set_interactivity(self, interactivity):
        """Adds interactivity syntax to the styling"""
        event_default = 'hover'
        if interactivity is None:
            return
        elif isinstance(interactivity, dict):
            self.interactivity = interactivity.get('event', event_default)
            self.header = interactivity.get('header')
        else:
            raise ValueError('`interactivity` must be a dictionary')


def _to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
