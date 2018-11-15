"""This module allows users to create interactive vector maps using CARTO VL.
The API for vector maps is broadly similar to :py:meth:`CartoContext.map
<cartoframes.context.CartoContext.map>`, with the exception that all styling
expressions are expected to be straight CARTO VL expressions. See examples in
the `CARTO VL styling guide
<https://carto.com/developers/carto-vl/guides/styling-points/>`__

Here is an example using the example CartoContext from the :py:class:`Examples
<cartoframes.examples.Examples>` class.

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


class BaseMaps(object):  # pylint: disable=too-few-public-methods
    """Supported CARTO vector basemaps. Read more about the styles in the
    `CARTO Basemaps repository <https://github.com/CartoDB/basemap-styles>`__.

    Attributes:
        darkmatter (str): CARTO's "Dark Matter" style basemap
        positron (str): CARTO's "Positron" style basemap
        voyager (str): CARTO's "Voyager" style basemap

    Example:
        Create an embedded map using CARTO's Positron style with no data layers

        .. code::

            from cartoframes.contrib import vector
            from cartoframes import CartoContext
            cc = CartoContext()
            vector.vmap([], context=cc, basemap=vector.BaseMaps.positron)
    """
    positron = 'Positron'
    darkmatter = 'DarkMatter'
    voyager = 'Voyager'


class QueryLayer(object):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """CARTO VL layer based on an arbitrary query against user database

    Args:
        query (str): Query against user database. This query must have the
          following columns included to successfully have a map rendered:
          `the_geom`, `the_geom_webmercator`, and `cartodb_id`. If columns are
          used in styling, they must be included in this query as well.
        color (str, optional): CARTO VL color styling for this layer. Valid
          inputs are simple web color names and hex values. For more advanced
          styling, see the CARTO VL guide on styling for more information:
          https://carto.com/developers/carto-vl/guides/styling-points/
        size (float or str, optional): CARTO VL width styling for this layer if
          points or lines (which are not yet implemented). Valid inputs are
          positive numbers or text expressions involving variables. To remain
          consistent with cartoframes' raster-based :py:class:`Layer
          <cartoframes.layer.Layer>` API, `size` is used here in place of
          `width`, which is the CARTO VL variable name for controlling the
          width of a point or line. Default size is 7 pixels wide.
        time (str, optional): Time expression to animate data. This is an alias
          for the CARTO VL `filter` style attribute. Default is no animation.
        strokeColor (str, optional): Defines the stroke color of polygons.
          Default is white.
        strokeWidth (float or str, optional): Defines the width of the stroke in
          pixels. Default is 1.
        interactivity (str, list, or dict, optional): This option adds
          interactivity (click or hover) to a layer. Defaults to ``click`` if
          one of the following inputs are specified:

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
                example_context,
                interactivity={
                    'cols': ['fare_amount', ],
                    'event': 'hover'
                }
            )
    """
    def __init__(self, query, color=None, size=None, time=None,
                 strokeColor=None, strokeWidth=None, interactivity=None):  # pylint: disable=invalid-name
        strconv = lambda x: str(x) if x is not None else None

        # data source
        self.query = query

        # style attributes
        self.color = color
        self.width = strconv(size)
        self.filter = time
        self.strokeColor = strokeColor  # pylint: disable=invalid-name
        self.strokeWidth = strconv(strokeWidth)  # pylint: disable=invalid-name

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
        if isinstance(interactivity, (tuple, list)):
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

def _get_html_doc(sources, bounds, creds=None, basemap=None):
    html_template = os.path.join(
        os.path.dirname(__file__),
        '..',
        'assets',
        'vector.html'
    )
    token = ''

    with open(html_template, 'r') as html_file:
        srcdoc = html_file.read()

    credentials = {
        'username': creds.username(),
        'api_key': creds.key(),
        'base_url': creds.base_url()
    }
    if isinstance(basemap, dict):
        token = basemap.get('token', '')
        if not 'style' in basemap:
            raise ValueError(
                'If basemap is a dict, it must have a `style` key'
            )
        if not token and basemap.get('style').startswith('mapbox://'):
            warn('A Mapbox style usually needs a token')
        basemap = basemap.get('style')

    return srcdoc.replace('@@SOURCES@@', json.dumps(sources)) \
                 .replace('@@BASEMAPSTYLE@@', basemap) \
                 .replace('@@MAPBOXTOKEN@@', token) \
                 .replace('@@CREDENTIALS@@', json.dumps(credentials)) \
                 .replace('@@BOUNDS@@', bounds)

class Layer(QueryLayer):  # pylint: disable=too-few-public-methods
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
                    strokeWidth=0),
                ],
                example_context)
    """
    def __init__(self, table_name, color=None, size=None, time=None,
                 strokeColor=None, strokeWidth=None, interactivity=None):  # pylint: disable=invalid-name
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

class LocalLayer(QueryLayer):  # pylint: disable=too-few-public-methods
    """Create a layer from a GeoDataFrame

    TODO: add support for filepath to a GeoJSON file, JSON/dict, or string

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
                 strokeColor=None, strokeWidth=None, interactivity=None):  # pylint: disable=invalid-name
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

def vmap(layers, context, size=(800, 400), basemap=BaseMaps.voyager):
    """CARTO VL-powered interactive map

    Args:
        layers (list of Layer-types): List of layers. One or more of
          :py:class:`Layer <cartoframes.contrib.vector.Layer>`,
          :py:class:`QueryLayer <cartoframes.contrib.vector.QueryLayer>`, or
          :py:class:`LocalLayer <cartoframes.contrib.vector.LocalLayer>`.
        context (:py:class:`CartoContext <cartoframes.context.CartoContext>`):
          A :py:class:`CartoContext <cartoframes.context.CartoContext>` instance
        basemap (str):
          - if a `str`, name of a CARTO vector basemap. One of `positron`,
            `voyager`, or `darkmatter` from the :obj:`BaseMaps` class
          - if a `dict`, Mapbox or other style as the value of the `style` key.
            If a Mapbox style, the access token is the value of the `token` key.

    Example:

        .. code::

            from cartoframes.contrib import vector
            from cartoframes import CartoContext
            cc = CartoContext(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            vector.vmap([vector.Layer('table in your account'), ], cc)

        CARTO basemap style.

        .. code::

            from cartoframes.contrib import vector
            from cartoframes import CartoContext
            cc = CartoContext(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            vector.vmap(
                [vector.Layer('table in your account'), ],
                context=cc,
                basemap=vector.BaseMaps.darkmatter
            )

        Custom basemap style. Here we use the Mapbox streets style, which
        requires an access token.

        .. code::

            from cartoframes.contrib import vector
            from cartoframes import CartoContext
            cc = CartoContext(
                base_url='https://<username>.carto.com',
                api_key='your api key'
            )
            vector.vmap(
                [vector.Layer('table in your account'), ],
                context=cc,
                basemap={
                    'style': 'mapbox://styles/mapbox/streets-v9',
                    'token: '<your mapbox token>'
                }
            )
    """
    non_local_layers = [
        layer for layer in layers
        if not isinstance(layer, LocalLayer)
    ]

    if non_local_layers:
        bounds = context._get_bounds(non_local_layers)  # pylint: disable=protected-access
        bounds = '[[{west}, {south}], [{east}, {north}]]'.format(**bounds)
    else:
        bounds = '[[-180, -85.0511], [180, 85.0511]]'

    jslayers = []
    for _, layer in enumerate(layers):
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
                _get_html_doc(jslayers, bounds, context.creds, basemap=basemap)
            )
        )
    return HTML(html)
