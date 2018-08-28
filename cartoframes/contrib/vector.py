"""This module allows users to create interactive vector maps using CARTO VL.
The API for vector maps is broadly similar to :py:meth:`CartoContext.map
<cartoframes.context.CartoContext.map>`, with the exception that all styling
expressions are expected to be straight CARTO VL expressions. See examples in
the `CARTO VL styling guide
<https://carto.com/developers/carto-vl/guides/styling-points/>`__
"""
import os
import json
from warnings import warn
from IPython.display import HTML
try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

from .. import utils

class QueryLayer(object):
    """CARTO VL layer based on an arbitrary query against user database

    Args:
        query (str): Query against user database. This query must have the
          the following columns included to successfully have a map rendered:
          `the_geom`, `the_geom_webmercator`, and `cartodb_id`. If columns are
          used in styling, they must be included in this query as well.
        color (str, optional): CARTO VL color styling for this layer. Valid
          inputs are simple web color names and hex values. For more advanced
          styling, see the CARTO VL guide on styling for more information:
          https://carto.com/developers/carto-vl/guides/styling-points/
        size (float or str, optional): CARTO VL width styling for this layer if
          points or lines (which are not yet implemented). Valid inputs are
          positive numbers or text expressions involving variables. To remain
          cosistent with cartoframes' raster-based :py:class:`Layer
          <cartoframes.layer.Layer>` API, `size` is used here in place of
          `width`, which is the CARTO VL variable name for controlling the
          width of a point or line. Default size is 7 pixels wide.
        time (str, optional): Time expression to animate data. This is an alias
          for the CARTO VL `filter` style attribute. Default is no animation.
        strokeColor (str, optional): Defines the stroke color of polygons.
          Default is white.
        strokeWidth (float or str, optional): Defines the width of the stroke in
          pixels. Default is 1.
        interactivity (str, list, or dict, optional): This option add
          interactivity (click or hover) to a layer. Defaults to click if one
          of the followring inputs are specified:

          - dict: If a :obj:`dict`, this must have the key `cols` with its value
            a list of columns. Optionally add `event` to choose ``hover`` or
            ``click``. Specifying a `header` key/value pair adds a header to
            the popup that will be rendered in HTML.
          - list: A list of valid column names in the data used for this layer
          - str: A column name in the data used in this layer

    Example:

        .. code::

            from cartoframes.examples import example_context
            from cartoframes.contrib import vector
            # create geometries from lng/lat columns
            q = '''
               SELECT *, ST_Transform(the_geom, 3857) as the_geom_webmercator
               FROM (
                   SELECT
                     CDB_LatLng(pickup_latitude, pickup_longitude) as the_geom,
                     fare_amount,
                     cartodb_id
                   FROM taxi_50k
               ) as _w
            '''
            vector.vmap(
                [vector.QueryLayer(q), ],
                example_context
            )
    """
    def __init__(self, query, color=None, size=None, time=None,
                 strokeColor=None, strokeWidth=None, interactivity=None):
        strconv = lambda x: str(x) if x is not None else None

        # data source
        self.query = query

        # style attributes
        self.color = color
        self.width = strconv(size)
        self.filter = time
        self.strokeColor = strokeColor
        self.strokeWidth = strconv(strokeWidth)

        # internal attributes
        self.orig_query = query
        self.is_basemap = False
        self.styling = ''
        self.interactivity = None
        self.header = None

        self._compose_style()

        # interactivity options
        self._set_interactivity(interactivity)

    def _compose_style(self):
        """Appends `prop` with `style` to layer styling"""
        valid_styles = (
            'color', 'width', 'filter', 'strokeWidth', 'strokeColor',
        )
        self.styling = '\n'.join(
            '{prop}: {style}'.format(prop=s, style=getattr(self, s))
            for s in valid_styles
            if getattr(self, s) is not None
        )

    def _set_interactivity(self, interactivity):
        """Adds interactivity syntax to the styling"""
        event_default = 'hover'
        if interactivity is None:
            return
        elif isinstance(interactivity, list) or isinstance(interactivity, tuple):
            self.interactivity = event_default
            interactive_cols = '\n'.join(
                '@{0}: ${0}'.format(col) for col in interactivity
            )
        elif isinstance(interactivity, str):
            self.interactivity = event_default
            interactive_cols = '@{0}: ${0}'.format(interactivity)
        elif isinstance(interactivity, dict):
            self.interactivity = interactivity.get('event', event_default)
            self.header = interactivity.get('header')
            interactive_cols = '\n'.join(
                '@{0}: ${0}'.format(col) for col in interactivity['cols']
            )
        else:
            raise ValueError('`interactivity` must be a str, a list of str, '
                             'or a dict with a `cols` key')

        self.styling = '\n'.join([interactive_cols, self.styling])

def _get_html_doc(sources, bounds, creds=None, local_sources=None, basemap=None):
    html_template = os.path.join(
        os.path.dirname(__file__),
        '..',
        'assets',
        'vector.html'
    )

    with open(html_template, 'r') as html_file:
        srcdoc = html_file.read()

    if basemap is None:
        basemap = 'DarkMatter'
    credentials = {} if creds is None else dict(user=creds.username(), api_key=creds.key())

    return (
        srcdoc\
            .replace('@@SOURCES@@', json.dumps(sources))
            .replace('@@BASEMAPSTYLE@@', basemap)
            .replace('@@CREDENTIALS@@', json.dumps(credentials))
            .replace('@@BOUNDS@@', bounds)
    )

class Layer(QueryLayer):
    """Layer from a table name. See :py:class:`QueryLayer
    <cartoframes.contrib.vector.QueryLayer>` for docs on the style attributes
    
    Example:

        Vizualize data from a table. Here we're using the example CartoContext.
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
                    strokeWidth=0),
                ],
                example_context)
    """
    def __init__(self, table_name, color=None, size=None, time=None,
                 strokeColor=None, strokeWidth=None, interactivity=None):
        self.table_source = table_name

        super(Layer, self).__init__(
            'SELECT * FROM {}'.format(table_name),
            color=color,
            size=size,
            time=time,
            strokeColor=strokeColor,
            strokeWidth=strokeWidth,
            interactivity=interactivity
        )

class LocalLayer(QueryLayer):
    """Create a layer from a GeoDataFrame

    TODO: add support for filepath to a geojson file, json/dict, or string

    See :obj:`QueryLayer` for the full styling documentation.

    Example:
        In this example, we grab data from the cartoframes example account
        using `read_mcdonals_nyc` to get McDonald's locations within New York
        City. Using the `decode_geom=True` argument, we decode the geometries
        into a form that works with GeoPandas. Finally, we pass the
        GeoDataFrame into :py:class:`LocalLayer
        <cartoframes.contrib.vector.LocalLayer>` to visualize.

        .. code::

            import geopandas as gpd
            from cartoframes.examples import read_mcdonalds_nyc, example_context
            from cartoframes.contrib import vector
            gdf = gpd.GeoDataFrame(read_mcdonalds_nyc(decode_geom=True))
            vector.vmap([vector.LocalLayer(gdf), ], context=example_context)
    """
    def __init__(self, dataframe, color=None, size=None, time=None,
                 strokeColor=None, strokeWidth=None, interactivity=None):
        if HAS_GEOPANDAS and isinstance(dataframe, geopandas.GeoDataFrame):
            self.geojson_str = dataframe.to_json()
        else:
            raise ValueError('LocalLayer only works with GeoDataFrames from '
                             'the geopandas package')

        super(LocalLayer, self).__init__(
            query=None,
            color=color,
            size=size,
            time=time,
            strokeColor=strokeColor,
            strokeWidth=strokeWidth,
            interactivity=interactivity
        )

def vmap(layers, context, size=(800, 400)):
    """CARTO VL-powered interactive map

    Args:
        layers (list of Layer-types): List of layers. One or more of
          :py:class:`Layer <cartoframes.contrib.vector.Layer>`,
          :py:class:`QueryLayer <cartoframes.contrib.vector.QueryLayer>`, or
          :py:class:`LocalLayer <cartoframes.contrib.vector.LocalLayer>`.
        context (:py:class:`CartoContext <cartoframes.context.CartoContext>`): A :py:class:`CartoContext <cartoframes.context.CartoContext>` instance

    Example:

        .. code::

            from cartoframes.contrib import vector
            from cartoframes import CartoContext
            cc = CartoContext(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            vector.vmap([vector.Layer('table in your account'), ], cc)
    """
    non_local_layers = [
        layer for layer in layers
        if not isinstance(layer, LocalLayer)
    ]

    if non_local_layers:
        bounds = context._get_bounds(non_local_layers)
        bounds =  '[[{west}, {south}], [{east}, {north}]]'.format(**bounds)
    else:
        bounds = '[[-180, -85.0511], [180, 85.0511]]'

    jslayers = []
    for idx, layer in enumerate(layers):
        is_local = isinstance(layer, LocalLayer)
        intera = (
            dict(event=layer.interactivity, header=layer.header)
            if layer.interactivity is not None
            else None
        )
        jslayers.append({
            'is_local': is_local,
            'styling': layer.styling,
            'source': layer.geojson_str if is_local else layer.query,
            'interactivity': intera
        })
    html = (
            '<iframe srcdoc="{content}" width={width} height={height}>'
            '</iframe>'
        ).format(
            width=size[0],
            height=size[1],
            content=utils.safe_quotes(
                _get_html_doc(jslayers, bounds, context.creds)
            )
    )
    return HTML(html)
