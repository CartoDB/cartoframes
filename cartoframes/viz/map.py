from __future__ import absolute_import

import collections
import numpy as np

from warnings import warn
from jinja2 import Environment, PackageLoader
from carto.exceptions import CartoException

from . import constants
from .basemaps import Basemaps
from .kuviz import KuvizPublisher, kuviz_to_dict
from .. import utils

WORLD_BOUNDS = [[-180, -90], [180, 90]]


class Map(object):
    """Map

    Args:
        layers (list of :py:class:`Layer <cartoframes.viz.Layer>`): List of
          layers. Zero or more of :py:class:`Layer <cartoframes.viz.Layer>`.
        basemap (str, optional):
          - if a `str`, name of a CARTO vector basemap. One of `positron`,
            `voyager`, or `darkmatter` from the :obj:`BaseMaps` class, or a
            hex value, rgb string, or other color expression from CARTO VL.
          - if a `dict`, Mapbox or other style as the value of the `style` key.
            If a Mapbox style, the access token is the value of the `token`
            key.
        bounds (dict or list, optional): a dict with `west`, `south`, `east`, `north`
          keys, or an array of floats in the following structure: [[west,
          south], [east, north]]. If not provided the bounds will be automatically
          calculated to fit all features.
        size (tuple, optional): a (width, height) pair for the size of the map.
          Default is (1024, 632).
        viewport (dict, optional): Properties for display of the map viewport.
          Keys can be `bearing` or `pitch`.
        default_legend (bool, optional): Default False. If True, a legend will
          display for each layer.
        show_info (bool, optional): Whether to display center and zoom information in the
          map or not. It is False by default.
        theme (string, optional): Use a different UI theme

    Examples:

        Basic usage.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Map(Layer('table in your account'))

        Display more than one layer on a map.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Map(layers=[
                Layer('table1'),
                Layer('table2')
            ])

        Change the CARTO basemap style.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer, basemaps

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Map(
                Layer('table in your account'),
                basemaps.darkmatter
            )

        Choose a custom basemap style. Here we use the Mapbox streets style,
        which requires an access token.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your CARTO API key'
            )

            basemap = {
                'style': 'mapbox://styles/mapbox/streets-v9',
                'token': 'your Mapbox token'
            }

            Map(
                Layer('table in your account'),
                basemap
            )

        Remove basemap and show a custom color.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            Map(
                Layer('table in your account'),
                basemap='yellow'  # None, False, 'white', 'rgb(255, 255, 0)'
            )

        Set custom bounds.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer

            set_default_credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )

            bounds = {
                'west': -10,
                'east': 10,
                'north': -10,
                'south': 10
            }

            # or bounds = [[-10, 10], [10, -10]]

            Map(
                Layer('table in your account'),
                bounds=bounds
            )

        Show the map center and zoom value on the map (lower left-hand corner).

        .. code::

            from cartoframes.auth import Credentials, set_default_credentials
            from cartoframes.viz import Map, Layer

            credentials = Credentials(
                base_url='https://your_user_name.carto.com',
                api_key='your api key'
            )
            set_default_credentials(credentials)

            Map(Layer('table in your account'), show_info=True)
    """

    def __init__(self,
                 layers=None,
                 basemap=Basemaps.positron,
                 bounds=None,
                 size=None,
                 viewport=None,
                 default_legend=False,
                 show_info=None,
                 theme=None,
                 **kwargs):

        self.layers = _init_layers(layers)
        self.basemap = basemap
        self.size = size
        self.viewport = viewport
        self.default_legend = default_legend
        self.show_info = show_info
        self.layer_defs = _get_layer_defs(self.layers)
        self.bounds = _get_bounds(bounds, self.layers)
        self.theme = _get_theme(theme, basemap)
        self._carto_vl_path = kwargs.get('_carto_vl_path', None)
        self._airship_path = kwargs.get('_airship_path', None)
        self._publisher = self._get_publisher()
        self._kuviz = None
        self._htmlMap = HTMLMap()

        self._htmlMap.set_content(
            layers=self.layer_defs,
            bounds=self.bounds,
            size=self.size,
            viewport=self.viewport,
            basemap=self.basemap,
            default_legend=self.default_legend,
            show_info=self.show_info,
            theme=self.theme,
            _carto_vl_path=self._carto_vl_path,
            _airship_path=self._airship_path)

    def _repr_html_(self):
        return self._htmlMap.html

    def publish(self, name, maps_api_key='default_public', credentials=None, password=None):
        """Publish the map visualization as a CARTO custom visualization (aka Kuviz).

        Args:
            name (str): The Kuviz name on CARTO
            maps_api_key (str, optional): A Regular API key with permissions
                to Maps API and datasets used by the map
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                A Credentials instance. If not provided, the credentials will be automatically
                obtained from the default credentials if available.
            password (str, optional): setting it your Kuviz will be protected by
                password. When someone will try to show the Kuviz, the password
                will be requested

        Example:

            Publishing the map visualization

            .. code::

                from cartoframes.viz import Map, Layer

                tmap = Map(Layer('tablename'))
                tmap.publish('Custom Map Title')

        """
        if not self._publisher.is_sync():
            raise CartoException('The map layers are not synchronized with CARTO. '
                                 'Please, use the `sync_data` method before publishing the map')

        if maps_api_key == 'default_public':
            self._validate_public_publication()

        self._publisher.set_credentials(credentials)
        html = self._get_publication_html(name, maps_api_key)
        self._kuviz = self._publisher.publish(html, name, password)
        return kuviz_to_dict(self._kuviz)

    def sync_data(self, table_name, credentials=None):
        """Synchronize datasets used by the map with CARTO.

        Args:
            table_name (str): Desired table name for the dataset on CARTO. If
                name does not conform to SQL naming conventions, it will be
                'normalized' (e.g., all lower case, adding `_` in place of spaces
                and other special characters.
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                A Credentials instance. If not provided, the credentials will be automatically
                obtained from the default credentials if available.
        """
        if not self._publisher.is_sync():
            self._publisher.sync_layers(table_name, credentials)

    def delete_publication(self):
        """Delete the published map Kuviz."""
        if self._kuviz:
            self._kuviz.delete()
            print("Publication '{n}' ({id}) deleted".format(n=self._kuviz.name, id=self._kuviz.id))
            self._kuviz = None

    def update_publication(self, name, password, maps_api_key='default_public'):
        """Update the published map Kuviz.

        Args:
            name (str): The Kuviz name on CARTO
            password (str): setting it your Kuviz will be protected by
                password and using `None` the Kuviz will be public
            maps_api_key (str, optional): A Regular API key with permissions
                to Maps API and datasets used by the map
        """
        if not self._kuviz:
            raise CartoException('The map has not been published. Use the `publish` method.')

        if not self._publisher.is_sync():
            raise CartoException('The map layers are not synchronized with CARTO. '
                                 'Please, use the `sync_data` method before publishing the map')

        if maps_api_key == 'default_public':
            self._validate_public_publication()

        self._kuviz.data = self._get_publication_html(name, maps_api_key)
        self._kuviz.name = name
        self._kuviz.password = password
        self._kuviz.save()
        return kuviz_to_dict(self._kuviz)

    @staticmethod
    def all_publications(credentials=None):
        """Get all map Kuviz published by the current user.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                A Credentials instance. If not provided, the credentials will be automatically
                obtained from the default credentials if available.
        """
        return KuvizPublisher.all(credentials)

    def _get_publication_html(self, name, maps_api_key):
        html_map = HTMLMap('viz/main.html.j2')
        html_map.set_content(
            layers=_get_layer_defs(self._publisher.get_layers(maps_api_key)),
            bounds=self.bounds,
            size=None,
            viewport=self.viewport,
            basemap=self.basemap,
            default_legend=self.default_legend,
            show_info=False,
            theme=self.theme,
            _carto_vl_path=self._carto_vl_path,
            _airship_path=self._airship_path,
            title=name,
            is_embed=True)

        return html_map.html

    def _get_publisher(self):
        return KuvizPublisher(self.layers)

    def _validate_public_publication(self):
        if not self._publisher.is_public():
            raise CartoException('The datasets used in your map are not public. '
                                 'You need add new Regular API key with permissions to Maps API and the datasets. '
                                 'You can do it from your CARTO dashboard or using the Auth API. You can get more '
                                 'info at https://carto.com/developers/auth-api/guides/types-of-API-Keys/')


def _get_bounds(bounds, layers):
    if bounds:
        return _format_bounds(bounds)
    else:
        return _compute_bounds(layers)


def _init_layers(layers):
    if layers is None:
        return []
    if not isinstance(layers, collections.Iterable):
        return [layers]
    else:
        return layers


def _get_layer_defs(layers):
    if layers is None:
        return None
    return list(map(_get_layer_def, layers))


def _get_layer_def(layer):
    return {
        'credentials': layer.credentials,
        'interactivity': layer.interactivity,
        'legend': layer.legend_info,
        'widgets': layer.widgets_info,
        'query': layer.source.query,
        'type': layer.source.type,
        'viz': layer.viz
    }


def _format_bounds(bounds):
    if bounds is None:
        return WORLD_BOUNDS
    if isinstance(bounds, list):
        return _format_list_bounds(bounds)
    elif isinstance(bounds, dict):
        return _format_dict_bounds(bounds)
    else:
        raise ValueError('Bounds must be a list or a dict')


def _format_list_bounds(bounds):
    if not (len(bounds) == 2 and len(bounds[0]) == 2 and len(bounds[1]) == 2):
        raise ValueError('Bounds list must have exactly four values in the '
                         'order: [[west, south], [east, north]]')

    return _clamp_and_format_bounds(
        bounds[0][0],
        bounds[0][1],
        bounds[1][0],
        bounds[1][1])


def _format_dict_bounds(bounds):
    if 'west' not in bounds or 'south' not in bounds or \
       'east' not in bounds or 'north' not in bounds:
        raise ValueError('Bounds must have "west", "south", "east" and '
                         '"north" properties')

    return _clamp_and_format_bounds(
        bounds.get('west'),
        bounds.get('east'),
        bounds.get('south'),
        bounds.get('north'))


def _clamp_and_format_bounds(west, south, east, north):
    west = _clamp(west, -180, 180)
    east = _clamp(east, -180, 180)
    south = _clamp(south, -90, 90)
    north = _clamp(north, -90, 90)

    return [[west, south], [east, north]]


def _clamp(value, minimum, maximum):
    return _conv2nan(max(minimum, min(value, maximum)))


def _conv2nan(val):
    """convert Nones to np.nans"""
    return np.nan if val is None else val


def _compute_bounds(layers):
    if layers is None or len(layers) == 0:
        return None

    bounds = _format_bounds(layers[0].bounds)

    for layer in layers[1:]:
        layer_bounds = _format_bounds(layer.bounds)

        if layer_bounds[0][0] < bounds[0][0]:
            bounds[0][0] = layer_bounds[0][0]

        if layer_bounds[0][1] < bounds[0][1]:
            bounds[0][1] = layer_bounds[0][1]

        if layer_bounds[1][0] > bounds[1][0]:
            bounds[1][0] = layer_bounds[1][0]

        if layer_bounds[1][1] > bounds[1][1]:
            bounds[1][1] = layer_bounds[1][1]

    return bounds


class HTMLMap(object):
    def __init__(self, template_path='viz/basic.html.j2'):
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
        self._template = self._env.get_template(template_path)

    def set_content(
        self, size, layers, bounds, viewport=None, basemap=None,
            default_legend=None, show_info=None, theme=None, _carto_vl_path=None,
            _airship_path=None, title='CARTOframes', is_embed=False):

        self.html = self._parse_html_content(
            size, layers, bounds, viewport, basemap, default_legend,
            show_info, theme, _carto_vl_path, _airship_path, title, is_embed)

    def _parse_html_content(
        self, size, layers, bounds, viewport, basemap=None, default_legend=None,
            show_info=None, theme=None, _carto_vl_path=None, _airship_path=None, title=None, is_embed=False):

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
            airship_module_path = constants.AIRSHIP_MODULE_URL
            airship_styles_path = constants.AIRSHIP_STYLES_URL
            airship_icons_path = constants.AIRSHIP_ICONS_URL
        else:
            airship_components_path = _airship_path + constants.AIRSHIP_COMPONENTS_DEV
            airship_bridge_path = _airship_path + constants.AIRSHIP_BRIDGE_DEV
            airship_module_path = _airship_path + constants.AIRSHIP_MODULE_DEV
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

        has_legends = any(layer['legend'] for layer in layers) or default_legend
        has_widgets = any(len(layer['widgets']) != 0 for layer in layers)

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
            has_widgets=has_widgets,
            default_legend=default_legend,
            show_info=show_info,
            theme=theme,
            carto_vl_path=carto_vl_path,
            airship_components_path=airship_components_path,
            airship_module_path=airship_module_path,
            airship_bridge_path=airship_bridge_path,
            airship_styles_path=airship_styles_path,
            airship_icons_path=airship_icons_path,
            title=title,
            is_embed=is_embed
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


def _get_theme(theme, basemap):
    if theme and theme not in constants.THEMES:
        raise ValueError(
            'This theme is not valid. Valid themes types are: {}.'.format(
                ', '.join(constants.THEMES)
            ))
    if not theme and basemap == Basemaps.darkmatter:
        return 'dark'

    return theme
