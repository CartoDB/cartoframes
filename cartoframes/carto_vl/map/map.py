import numpy as np
import os
import json

from warnings import warn
from IPython.display import HTML

from cartoframes import utils
from ..basemap.basemap import Basemap
from ..layer.layer import Layer
from ..layer.local_layer import LocalLayer
from ..layer.query_layer import QueryLayer

# CARTO VL
_DEFAULT_CARTO_VL_PATH = 'https://libs.cartocdn.com/carto-vl/v1.1.1/carto-vl.min.js'

# AIRSHIP
_AIRSHIP_SCRIPT = '/packages/components/dist/airship.js'
_AIRSHIP_BRIDGE_SCRIPT = '/packages/bridge/dist/asbridge.js'
_AIRSHIP_STYLE = '/packages/styles/dist/airship.css'
_AIRSHIP_ICONS_STYLE = '/packages/icons/dist/icons.css'

_DEFAULT_AIRSHIP_COMPONENTS_PATH = 'https://libs.cartocdn.com/airship-components/v1.0.3/airship.js'
_DEFAULT_AIRSHIP_BRIDGE_PATH = 'https://libs.cartocdn.com/airship-bridge/v1.0.3/asbridge.js'
_DEFAULT_AIRSHIP_STYLES_PATH = 'https://libs.cartocdn.com/airship-style/v1.0.3/airship.css'
_DEFAULT_AIRSHIP_ICONS_PATH = 'https://libs.cartocdn.com/airship-icons/v1.0.3/icons.css'


class Map(object):
    """CARTO VL-powered interactive map

    Args:
        layers (list of Layer-types): List of layers. One or more of
          :py:class:`Layer <cartoframes.contrib.vector.Layer>`,
          :py:class:`QueryLayer <cartoframes.contrib.vector.QueryLayer>`, or
          :py:class:`LocalLayer <cartoframes.contrib.vector.LocalLayer>`.
        context (:py:class:`CartoContext <cartoframes.context.CartoContext>`):
          A :py:class:`CartoContext <cartoframes.context.CartoContext>`
          instance
        size (tuple of int): a (width, height) pair for the size of the map.
          Default is (1024, 632)
        basemap (str):
          - if a `str`, name of a CARTO vector basemap. One of `positron`,
            `voyager`, or `darkmatter` from the :obj:`BaseMaps` class
          - if a `dict`, Mapbox or other style as the value of the `style` key.
            If a Mapbox style, the access token is the value of the `token`
            key.
        bounds (dict or list): a dict with `east`,`north`,`west`,`south`
          properties, or a list of floats in the following order: [west,
          south, east, north]. If not provided the bounds will be automatically
          calculated to fit all features.

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

        Custom bounds

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
                bounds={'west': -10, 'east': 10, 'north': -10, 'south': 10}
            )
    """

    @utils.temp_ignore_warnings
    def __init__(self,
                 layers,
                 context,
                 size=(1024, 632),
                 basemap=Basemap.voyager,
                 bounds=None,
                 template=None):

        self.layers = layers
        self.context = context
        self.size = size
        self.basemap = basemap
        self.bounds = bounds
        self.template = template

        _carto_vl_path = kwargs.get('_carto_vl_path', _DEFAULT_CARTO_VL_PATH)
        _airship_path = kwargs.get('_airship_path', None)

        if bounds:
            bounds = _format_bounds(bounds)
        else:
            bounds = _get_super_bounds(layers, context)

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
                'source': layer._geojson_str if is_local else layer.query,
                'interactivity': intera,
                'legend': layer.legend
            })

        html = ("""
            <iframe
                srcdoc="{content}"
                width="{width}"
                height="{height}">
            </iframe>
        """)

        html_doc = _get_html_doc(
            jslayers,
            bounds,
            context.creds,
            basemap,
            _carto_vl_path,
            _airship_path)

        content = utils.safe_quotes(html_doc)
        html.format(width=size[0], height=size[1], content)

        self.template = HTML(html)


def init(self):
    return self.template


def _get_html_doc(sources,
                  bounds,
                  creds=None,
                  basemap=None,
                  _carto_vl_path=_DEFAULT_CARTO_VL_PATH,
                  _airship_path=None):

    html_template = os.path.join(
        os.path.dirname(__file__),
        '..',
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
        if 'style' not in basemap:
            raise ValueError(
                'If basemap is a dict, it must have a `style` key'
            )
        if not token and basemap.get('style').startswith('mapbox://'):
            warn('A Mapbox style usually needs a token')
        basemap = basemap.get('style')

    if (_airship_path is None):
        airship_components_path = _DEFAULT_AIRSHIP_COMPONENTS_PATH
        airship_bridge_path = _DEFAULT_AIRSHIP_BRIDGE_PATH
        airship_styles_path = _DEFAULT_AIRSHIP_STYLES_PATH
        airship_icons_path = _DEFAULT_AIRSHIP_ICONS_PATH
    else:
        airship_components_path = _airship_path + _AIRSHIP_SCRIPT
        airship_bridge_path = _airship_path + _AIRSHIP_BRIDGE_SCRIPT
        airship_styles_path = _airship_path + _AIRSHIP_STYLE
        airship_icons_path = _airship_path + _AIRSHIP_ICONS_STYLE

    return srcdoc.replace('@@SOURCES@@', json.dumps(sources)) \
        .replace('@@BASEMAPSTYLE@@', basemap) \
        .replace('@@MAPBOXTOKEN@@', token) \
        .replace('@@CREDENTIALS@@', json.dumps(credentials)) \
        .replace('@@BOUNDS@@', bounds) \
        .replace('@@CARTO_VL_PATH@@', _carto_vl_path) \
        .replace('@@AIRSHIP_COMPONENTS_PATH@@', airship_components_path) \
        .replace('@@AIRSHIP_BRIDGE_PATH@@', airship_bridge_path) \
        .replace('@@AIRSHIP_STYLES_PATH@@', airship_styles_path) \
        .replace('@@AIRSHIP_ICONS_PATH@@', airship_icons_path)


def _format_bounds(bounds):
    if isinstance(bounds, dict):
        return _dict_bounds(bounds)

    return _list_bounds(bounds)


def _list_bounds(bounds):
    if len(bounds) != 4:
        raise ValueError('bounds list must have exactly four values in the '
                         'order: [west, south, east, north]')

    return _dict_bounds({
        'west': bounds[0],
        'south': bounds[1],
        'east': bounds[2],
        'north': bounds[3]
    })


def _dict_bounds(bounds):
    if 'west' not in bounds or 'east' not in bounds or 'north' not in bounds\
            or 'south' not in bounds:
        raise ValueError('bounds must have east, west, north and '
                         'south properties')

    return '[[{west}, {south}], [{east}, {north}]]'.format(**bounds)


def _get_super_bounds(layers, context):
    """"""
    hosted_layers = [
        layer for layer in layers
        if not isinstance(layer, LocalLayer)
    ]
    local_layers = [
        layer for layer in layers
        if isinstance(layer, LocalLayer)
    ]
    hosted_bounds = dict.fromkeys(['west', 'south', 'east', 'north'])
    local_bounds = dict.fromkeys(['west', 'south', 'east', 'north'])

    if hosted_layers:
        hosted_bounds = context._get_bounds(hosted_layers)
    if local_layers:
        local_bounds = _get_bounds_local(local_layers)

    bounds = _combine_bounds(hosted_bounds, local_bounds)

    return _format_bounds(bounds)


def _get_bounds_local(layers):
    """Aggregates bounding boxes of all local layers

        return: dict of bounding box of all bounds in layers
    """
    if not layers:
        return {'west': None, 'south': None, 'east': None, 'north': None}

    bounds = layers[0].bounds

    for layer in layers[1:]:
        bounds = np.concatenate(
            (
                np.minimum(
                    bounds[:2],
                    layer.bounds[:2]
                ),
                np.maximum(
                    bounds[2:],
                    layer.bounds[2:]
                )
            )
        )

    return dict(zip(['west', 'south', 'east', 'north'], bounds))


def _combine_bounds(bbox1, bbox2):
    """Takes two bounding boxes dicts and gives a new bbox that encompasses
    them both"""
    WORLD = {'west': -180, 'south': -85.1, 'east': 180, 'north': 85.1}
    ALL_KEYS = set(WORLD.keys())

    def dict_all_nones(bbox_dict):
        """Returns True if all dict values are None"""
        return all(v is None for v in bbox_dict.values())

    # if neither are defined, use the world
    if not bbox1 and not bbox2:
        return WORLD
    # if all nones, use the world
    if dict_all_nones(bbox1) and dict_all_nones(bbox2):
        return WORLD

    assert ALL_KEYS == set(bbox1.keys()) and ALL_KEYS == set(bbox2.keys()),\
        'Input bounding boxes must have the same dictionary keys'
    # create dict with cardinal directions and None-valued keys
    outbbox = dict.fromkeys(['west', 'south', 'east', 'north'])

    def conv2nan(val):
        """convert Nones to np.nans"""
        return np.nan if val is None else val

    # set values and/or defaults
    for coord in ('north', 'east'):
        outbbox[coord] = np.nanmax([
                conv2nan(bbox1[coord]),
                conv2nan(bbox2[coord])
            ])
    for coord in ('south', 'west'):
        outbbox[coord] = np.nanmin([
                conv2nan(bbox1[coord]),
                conv2nan(bbox2[coord])
            ])

    return outbbox
