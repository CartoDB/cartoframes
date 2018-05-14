import os
import json
import IPython
try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

from .. import utils

class QueryLayer:
    def __init__(self, query, color=None, size=None, time=None):
        self.query = query
        self.color = color
        self.size = size
        self.time = time
        self.orig_query = query
        self.is_basemap = False
        self.styling = ''

        # todo add torque
        if self.color:
            self.styling += '\ncolor: {}'.format(self.color)
        if self.size:
            self.styling += '\nwidth: {}'.format(self.size)
        if self.time:
            self.styling += '\nfilter: {}'.format(self.time)

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
        if isinstance(dataframe, geopandas.GeoDataFrame):
            self.geojson_str = dataframe.to_json()
        else:
            raise ValueError('LocalLayer only works with GeoDataFrames')

        super(LocalLayer, self).__init__(
            query=None,
            time=time,
            color=color,
            size=size
        )

def ccmap(layers, context):
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
    return IPython.display.HTML(html)
