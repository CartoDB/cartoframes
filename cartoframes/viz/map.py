from __future__ import absolute_import

import collections
import numpy as np
from warnings import warn
from jinja2 import Environment, PackageLoader

from . import constants
from .basemaps import Basemaps
from .source import SourceType
from .. import utils

# TODO: refactor


class Map(object):
    """Map

    Args:
        layers (list of Layer-types): List of layers. One or more of
          :py:class:`Layer <cartoframes.viz.Layer>`.
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
        size (tuple of int): a (width, height) pair for the size of the map.
          Default is (1024, 632)
        show_info (bool, optional): Whether to display center and zoom information in the
          map or not. It is False by default.

    Example:

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Map, Layer

            set_default_context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Map(Layer('table in your account'))

        CARTO basemap style.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Map, Layer, basemaps

            set_default_context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Map(
                Layer('table in your account'),
                basemaps.darkmatter
            )

        Custom basemap style. Here we use the Mapbox streets style, which
        requires an access token.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Map, Layer, basemaps

            set_default_context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            basemap = {
                'style': 'mapbox://styles/mapbox/streets-v9',
                'token: '<your mapbox token>'
            }

            Map(
                Layer('table in your account'),
                basemap
            )

        Color basemap style.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Map, Layer, basemaps

            set_default_context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Map(
                Layer('table in your account'),
                basemap='yellow'  # None, False, 'white', 'rgb(255, 255, 0)'
            )

        Custom bounds.

        .. code::

            from cartoframes.auth import set_default_context
            from cartoframes.viz import Map, Layer

            set_default_context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            bounds = {
                'west': -10,
                'east': 10,
                'north': -10,
                'south': 10
            }

            Map(
                Layer('table in your account'),
                bounds=bounds
            )

        Show map center and zoom values

        .. code::

            from cartoframes.auth import Context, set_default_context
            from cartoframes.viz import Map, Layer

            context = Context(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            set_default_context(context)

            Map(Layer('table in your account'), show_info=True)
    """

    def __init__(self,
                 layers=None,
                 basemap=Basemaps.darkmatter,
                 bounds=None,
                 size=None,
                 viewport=None,
                 default_legend=False,
                 show_info=None,
                 **kwargs):

        self.layers = _init_layers(layers)
        self.basemap = basemap
        self.size = size
        self.viewport = viewport
        self.default_legend = default_legend
        self.show_info = show_info
        self.layer_defs = _get_layer_defs(self.layers)
        self.bounds = _get_bounds(bounds, self.layers)
        self._carto_vl_path = kwargs.get('_carto_vl_path', None)
        self._airship_path = kwargs.get('_airship_path', None)

        self._htmlMap = HTMLMap()
        self._htmlMap.set_content(
            layers=self.layer_defs,
            bounds=self.bounds,
            size=self.size,
            viewport=self.viewport,
            basemap=self.basemap,
            default_legend=self.default_legend,
            show_info=self.show_info,
            _carto_vl_path=self._carto_vl_path,
            _airship_path=self._airship_path)

    def _repr_html_(self):
        return self._htmlMap.html

    def publish(self):
        pass


def _get_bounds(bounds, layers):
    return (
        _format_bounds(bounds)
        if bounds
        else _get_super_bounds(layers)
    )


def _init_layers(layers):
    if layers is None:
        return []
    if not isinstance(layers, collections.Iterable):
        return [layers]
    else:
        # Reverse layers
        return layers[::-1]


def _get_layer_defs(layers):
    if layers is None:
        return None
    return list(map(_get_layer_def, layers))


def _get_layer_def(layer):
    return {
        'credentials': layer.source.credentials,
        'interactivity': layer.interactivity,
        'legend': layer.legend_info,
        'query': layer.source.query,
        'type': layer.source.type,
        'viz': layer.viz
    }


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


def _get_super_bounds(layers):
    """"""
    # TODO: refactor this method:
    # Compute the bounds in the source class
    if layers:
        hosted_layers = [
            layer for layer in layers
            if layer.source.type != SourceType.GEOJSON
        ]
        local_layers = [
            layer for layer in layers
            if layer.source.type == SourceType.GEOJSON
        ]
    else:
        hosted_layers = []
        local_layers = []

    hosted_bounds = dict.fromkeys(['west', 'south', 'east', 'north'])
    local_bounds = dict.fromkeys(['west', 'south', 'east', 'north'])

    if hosted_layers:
        hosted_bounds = _get_bounds_hosted(hosted_layers)

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

    if bounds is None:
        return {'west': None, 'south': None, 'east': None, 'north': None}

    return dict(zip(['west', 'south', 'east', 'north'], bounds))


def _get_bounds_hosted(layers):
    """Aggregates bounding boxes of all hosted layers

        return: dict of bounding box of all bounds in layers
    """
    if not layers:
        return {'west': None, 'south': None, 'east': None, 'north': None}

    context = layers[0].source.context
    bounds = context and context._get_bounds([layers[0]])

    for layer in layers[1:]:
        context = layer.source.context
        next_bounds = context and context._get_bounds([layer])
        bounds = _combine_bounds(bounds, next_bounds)

    return bounds


def _combine_bounds(bbox1, bbox2):
    """Takes two bounding boxes dicts and gives a new bbox that encompasses
    them both"""
    WORLD = {'west': -180, 'south': -85.1, 'east': 180, 'north': 85.1}
    ALL_KEYS = set(WORLD.keys())

    # if neither are defined, use the world
    if not bbox1 and not bbox2:
        return WORLD
    # if all nones, use the world
    if _dict_all_nones(bbox1) and _dict_all_nones(bbox2):
        return WORLD

    # if one is none return the other
    if not bbox1 or not bbox2:
        return bbox1 or bbox2

    assert ALL_KEYS == set(bbox1.keys()) and ALL_KEYS == set(bbox2.keys()),\
        'Input bounding boxes must have the same dictionary keys'
    # create dict with cardinal directions and None-valued keys
    outbbox = dict.fromkeys(['west', 'south', 'east', 'north'])

    # set values and/or defaults
    for coord in ('north', 'east'):
        outbbox[coord] = np.nanmax([
            _conv2nan(bbox1[coord]),
            _conv2nan(bbox2[coord])
        ])
    for coord in ('south', 'west'):
        outbbox[coord] = np.nanmin([
            _conv2nan(bbox1[coord]),
            _conv2nan(bbox2[coord])
        ])

    return outbbox


def _dict_all_nones(bbox_dict):
    """Returns True if all dict values are None"""
    return bbox_dict and all(v is None for v in bbox_dict.values())


def _conv2nan(val):
    """convert Nones to np.nans"""
    return np.nan if val is None else val


class HTMLMap(object):
    def __init__(self):
        self.width = None
        self.height = None
        self.srcdoc = None

        self._env = Environment(
            loader=PackageLoader('cartoframes', 'assets/templates'),
            autoescape=True
        )

        self._env.filters['quot'] = _quote_filter
        self._env.filters['iframe_size'] = _iframe_size_filter
        self._env.filters['clear_none'] = _clear_none_filter

        self.html = None
        self._template = self._env.get_template('viz/basic.html.j2')

    def set_content(
        self, size, layers, bounds, viewport=None, basemap=None,
            default_legend=None, show_info=None,
            _carto_vl_path=None, _airship_path=None):

        self.html = self._parse_html_content(
            size, layers, bounds, viewport, basemap, default_legend, show_info,
            _carto_vl_path, _airship_path)

    def _parse_html_content(
        self, size, layers, bounds, viewport, basemap=None, default_legend=None,
            show_info=None, _carto_vl_path=None, _airship_path=None):

        token = ''
        basecolor = ''

        if basemap is None:
            # No basemap
            basecolor = 'white'
            basemap = ''
        elif isinstance(basemap, str):
            if basemap not in [Basemaps.voyager, Basemaps.positron, Basemaps.darkmatter]:
                # Basemap is a color
                basecolor = basemap
                basemap = ''
        elif isinstance(basemap, dict):
            token = basemap.get('token', '')
            if 'style' in basemap:
                basemap = basemap.get('style')
                if not token and basemap.get('style').startswith('mapbox://'):
                    warn('A Mapbox style usually needs a token')
            else:
                raise ValueError(
                    'If basemap is a dict, it must have a `style` key'
                )

        if _carto_vl_path is None:
            carto_vl_path = constants.CARTO_VL_URL
        else:
            carto_vl_path = _carto_vl_path + constants.CARTO_VL_DEV

        if _airship_path is None:
            airship_components_path = constants.AIRSHIP_COMPONENTS_URL
            airship_bridge_path = constants.AIRSHIP_BRIDGE_URL
            airship_styles_path = constants.AIRSHIP_STYLES_URL
            airship_icons_path = constants.AIRSHIP_ICONS_URL
        else:
            airship_components_path = _airship_path + constants.AIRSHIP_COMPONENTS_DEV
            airship_bridge_path = _airship_path + constants.AIRSHIP_BRIDGE_DEV
            airship_styles_path = _airship_path + constants.AIRSHIP_STYLES_DEV
            airship_icons_path = _airship_path + constants.AIRSHIP_ICONS_DEV

        camera = None
        if viewport is not None:
            camera = {
                'center': _get_center(viewport),
                'zoom': viewport.get('zoom'),
                'bearing': viewport.get('bearing'),
                'pitch': viewport.get('pitch')
            }

        has_legends = any(layer['legend'] is not None for layer in layers) or default_legend

        return self._template.render(
            width=size[0] if size is not None else None,
            height=size[1] if size is not None else None,
            layers=layers,
            basemap=basemap,
            basecolor=basecolor,
            mapboxtoken=token,
            bounds=bounds,
            camera=camera,
            has_legends=has_legends,
            default_legend=default_legend,
            show_info=show_info,
            carto_vl_path=carto_vl_path,
            airship_components_path=airship_components_path,
            airship_bridge_path=airship_bridge_path,
            airship_styles_path=airship_styles_path,
            airship_icons_path=airship_icons_path
        )

    def _repr_html_(self):
        return self.html


def _quote_filter(value):
    return utils.safe_quotes(value.unescape())


def _iframe_size_filter(value):
    if isinstance(value, str):
        return value

    return '%spx;' % value


def _clear_none_filter(value):
    return dict(filter(lambda item: item[1] is not None, value.items()))


def _get_center(center):
    if 'lng' not in center or 'lat' not in center:
        return None

    return [center.get('lng'), center.get('lat')]
