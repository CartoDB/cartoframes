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
        size (int or str, optional): CARTO VL width styling for this layer if
          points or lines (which are not yet implemented). Valid inputs are
          positive numbers or text expressions involving variables.
    """
    def __init__(self, query, color=None, size=None, time=None,
                 strokeColor=None, strokeWidth=None):
        self.query = query
        self.color = color
        self.width = size
        self.filter = time
        self.strokeColor = strokeColor
        self.strokeWidth = strokeWidth
        self.orig_query = query
        self.is_basemap = False
        self.styling = ''

        self._update_style()

    def _update_style(self):
        """Appends `prop` with `style` to layer styling"""
        valid_styles = (
            'color', 'width', 'filter', 'strokeWidth', 'strokeColor',
        )
        self.styling = '\n'.join(
            '{prop}: {style}'.format(prop=s, style=getattr(self, s))
            for s in valid_styles
            if getattr(self, s)
        )
        print(self.styling)

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
    def __init__(self, table_name, color=None, size=None, time=None):
        self.table_source = table_name

        super(Layer, self).__init__(
            'SELECT * FROM {}'.format(table_name),
            time=time,
            color=color,
            size=size
        )

class LocalLayer(QueryLayer):
    def __init__(self, dataframe, color=None, size=None, time=None):
        if HAS_GEOPANDAS and isinstance(dataframe, geopandas.GeoDataFrame):
            self.geojson_str = dataframe.to_json()
        else:
            raise ValueError('LocalLayer only works with GeoDataFrames')

        super(LocalLayer, self).__init__(
            query=None,
            time=time,
            color=color,
            size=size
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
    html = (
        '<iframe srcdoc="{content}" width=800 height=400>'
        '</iframe>'
    ).format(content=utils.safe_quotes(
        _get_html_doc(jslayers, bounds, context.creds)
    ))
    return HTML(html)
