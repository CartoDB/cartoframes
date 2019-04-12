from __future__ import absolute_import
from .. import defaults


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
            from cartoframes import carto_vl as vl
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

            vl.Map(
                [vl.QueryLayer(query)],
                example_context,
                variables={
                  'fare_amount': 'fare_amount'
                },
                interactivity={
                    'cols': ['fare_amount'],
                    'event': 'hover'
                }
            )
    """

    def __init__(self,
                 query,
                 style=None,
                 variables=None,
                 interactivity=None,
                 legend=None):

        # context attributes
        self.orig_query = query
        self.is_basemap = False

        # map attributes
        self.query = query
        self.style = _parse_style_properties(style)
        self.variables = _parse_variables(variables)
        self.interactivity = _parse_interactivity(interactivity)
        self.legend = legend
        self.viz = _set_viz(self.variables, self.style)


def _convstr(obj):
    """convert all types to strings or None"""
    return str(obj) if obj is not None else None


def _to_camel_case(text):
    """convert properties to camelCase"""
    components = text.split('-')
    return components[0] + ''.join(x.title() for x in components[1:])


def _parse_style_properties(style):
    """Adds style properties to the styling"""
    if style is None:
        return ''
    elif isinstance(style, dict):
        return _parse_style_properties_dict(style)
    elif isinstance(style, (tuple, list)):
        return _parse_style_properties_list(style)
    elif isinstance(style, str):
        return style
    else:
        raise ValueError('`style` must be a dictionary, a list or a string')


def _parse_style_properties_dict(style):
    return '\n'.join(
        '{name}: {value}'.format(
          name=_to_camel_case(style_prop),
          value=_convstr(style.get(style_prop))
        )
        for style_prop in style
        if style_prop in defaults._STYLE_PROPERTIES
        and style.get(style_prop) is not None
        )


def _parse_style_properties_list(style):
    return '\n'.join(
      '{name}: {value}'.format(
          name=_to_camel_case(style_prop[0]),
          value=_convstr(style_prop[1])
      ) for style_prop in style if style_prop[0] in defaults._STYLE_PROPERTIES)


def _parse_variables(variables):
    """Adds variables to the styling"""
    if variables is None:
        return None
    elif isinstance(variables, (tuple, list)):
        return _parse_variables_list(variables)
    elif isinstance(variables, dict):
        return _parse_variables_dict(variables)
    else:
        raise ValueError('`variables` must be a list of [ name, value ]')


def _parse_variables_list(variables):
    return '\n'.join(
        '@{name}: {value}'.format(
            name=variable[0],
            value=variable[1]
        ) for variable in variables)


def _parse_variables_dict(variables):
    return '\n'.join(
        '@{name}: {value}'.format(
          name=variable,
          value=variables.get(variable)
        )
        for variable in variables)


def _parse_interactivity(interactivity):
    """Adds interactivity syntax to the styling"""
    event_default = 'hover'

    if interactivity is None:
        return None
    elif isinstance(interactivity, dict):
        return {
          'event': interactivity.get('event', event_default),
          'header': interactivity.get('header', None),
          'values': interactivity.get('values', None)
        }
    elif interactivity is True:
        return {
          'event': event_default,
        }
    else:
        raise ValueError('`interactivity` must be a dictionary')


def _set_viz(variables, style):
    if variables and style:
        return '\n'.join([variables, style])
    elif variables:
        return variables
    else:
        return style
