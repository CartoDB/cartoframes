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

class QueryLayer:
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
          cosistent with cartoframes' raster-based :obj:`Layer` API, `size` is
          used here in place of `width`, which is the CARTO VL variable name
          for controlling the width of a point or line. Default size is 7
          pixels wide.
        time (str, optional): Time expression to animate data. This is an alias
          for the CARTO VL `filter` style attribute. Default is no animation.
        strokeColor (str, optional): Defines the stroke color of polygons.
          Default is white.
        strokeWidth (float or str, optional): Defines the width of the stroke in
          pixels. Default is 1.
    """
    def __init__(self, query, color=None, size=None, time=None,
                 strokeColor=None, strokeWidth=None):
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

        self._compose_style()

    def _compose_style(self):
        """Appends `prop` with `style` to layer styling"""
        valid_styles = (
            'color', 'width', 'filter', 'strokeWidth', 'strokeColor',
        )
        self.styling = '\n'.join(
            '{prop}: {style}'.format(prop=s, style=getattr(self, s))
            for s in valid_styles
            if hasattr(self, s)
        )

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
    """Layer from a table name. See :obj:`QueryLayer` for docs on the style
    attributes"""
    def __init__(self, table_name, color=None, size=None, time=None,
                 strokeColor=None, strokeWidth=None):
        self.table_source = table_name

        super(Layer, self).__init__(
            'SELECT * FROM {}'.format(table_name),
            color=color,
            size=size,
            time=time,
            strokeColor=strokeColor,
            strokeWidth=strokeWidth
        )

class LocalLayer(QueryLayer):
    """Create a layer from a GeoDataFrame

    TODO: add support for filepath to a geojson file, json/dict, or string

    See :obj:`QueryLayer` for the full styling documentation.
    """
    def __init__(self, dataframe, color=None, size=None, time=None,
                 strokeColor=None, strokeWidth=None):
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
            strokeWidth=strokeWidth
        )

def vmap(layers, context):
    """CARTO VL-powered interactive map

    Args:
        layers (list of Layer-types): List of layers. One or more of
          :obj:`Layer`, :obj:`QueryLayer`, or :obj:`LocalLayer`.
        context (:obj:`CartoContext`): A :obj:`CartoContext` instance
    """
    warn(
        'The `vector` module is in contrib, meaning that all features are '
        'subject to change as they are experimental features'
    )
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
        jslayers.append({
            'is_local': is_local,
            'styling': layer.styling,
            'source': layer.geojson_str if is_local else layer.query,
        })
    html = '<iframe srcdoc="{content}" width=800 height=400></iframe>'.format(
        content=utils.safe_quotes(
            _get_html_doc(jslayers, bounds, context.creds)
        )
    )
    return HTML(html)
