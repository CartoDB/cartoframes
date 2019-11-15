from __future__ import absolute_import

import collections
from warnings import warn

import numpy as np
from carto.exceptions import CartoException

from . import constants
from .basemaps import Basemaps
from .html import HTMLMap
from .kuviz import KuvizPublisher
from ..utils.utils import get_center

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
        default_legend (bool, optional): Default False. If True, it displays the map title.
          Therefore, it needs the `title` value to be defined.
        show_info (bool, optional): Whether to display center and zoom information in the
          map or not. It is False by default.
        is_static (bool, optional): Default False. If True, instead of showing and interactive
          map, a png image will be displayed.
        theme (string, optional): Use a different UI theme
        title (string, optional): Title to label the map
        description (string, optional): Text that describes the map and will be displayed in the
          default legend after the title.

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
                 title=None,
                 description=None,
                 is_static=None,
                 **kwargs):

        self._validate_default_legend(default_legend, title)

        self.layers = _init_layers(layers)
        self.basemap = basemap
        self.size = size
        self.viewport = viewport
        self.default_legend = default_legend
        self.title = title
        self.description = description
        self.show_info = show_info
        self.layer_defs = _get_layer_defs(self.layers)
        self.bounds = _get_bounds(bounds, self.layers)
        self.theme = _get_theme(theme, basemap)
        self.is_static = is_static
        self.token = get_token(basemap)
        self.basecolor = get_basecolor(basemap)

        self._carto_vl_path = kwargs.get('_carto_vl_path', None)
        self._airship_path = kwargs.get('_airship_path', None)

        self._publisher = None
        self._kuviz = None

        self.camera = None
        if viewport is not None:
            self.camera = {
                'center': get_center(viewport),
                'zoom': viewport.get('zoom'),
                'bearing': viewport.get('bearing'),
                'pitch': viewport.get('pitch')
            }

    def _repr_html_(self):
        self._html_map = HTMLMap()

        self._html_map.set_content(
            layers=self.layer_defs,
            bounds=self.bounds,
            size=self.size,
            camera=self.camera,
            basemap=self.basemap,
            default_legend=self.default_legend,
            show_info=self.show_info,
            theme=self.theme,
            title=self.title,
            description=self.description,
            is_static=self.is_static,
            _carto_vl_path=self._carto_vl_path,
            _airship_path=self._airship_path)

        return self._html_map.html

    def get_content(self):
        has_legends = any(layer['legend'] for layer in self.layer_defs) or self.default_legend
        has_widgets = any(len(layer['widgets']) != 0 for layer in self.layer_defs)

        return {
            'layers': self.layer_defs,
            'bounds': self.bounds,
            'size': self.size,
            'viewport': self.viewport,
            'camera': self.camera,
            'basemap': self.basemap,
            'basecolor': self.basecolor,
            'token': self.token,
            'default_legend': self.default_legend,
            'show_info': self.show_info,
            'has_legends': has_legends,
            'has_widgets': has_widgets,
            'theme': self.theme,
            'title': self.title,
            'description': self.description,
            'is_static': self.is_static,
            '_carto_vl_path': self._carto_vl_path,
            '_airship_path': self._airship_path
        }

    def publish(self, name, table_name=None, credentials=None, password=None):
        """Publish the map visualization as a CARTO custom visualization (aka Kuviz).

        Args:
            name (str): The Kuviz name on CARTO
            table_name (str, optional): Desired table name for the dataset on CARTO.
                It is required working with local data (we need to upload it to CARTO)
                If name does not conform to SQL naming conventions, it will be
                'normalized' (e.g., all lower case, adding `_` in place of spaces
                and other special characters.
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                A Credentials instance. If not provided, the credentials will be automatically
                obtained from the default credentials if available. It is used to create the
                publication and also to save local data (if exists) into your CARTO account
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
        self._publisher = _get_publisher(table_name, credentials)
        self._publisher.set_layers(self.layers, name, table_name)

        html = self._get_publication_html(name)
        return self._publisher.publish(html, name, password)

    def delete_publication(self):
        """Delete the published map Kuviz."""
        return self._publisher.delete()

    def update_publication(self, name, password):
        """Update the published map Kuviz.

        Args:
            name (str): The Kuviz name on CARTO
            password (str): setting it your Kuviz will be protected by
                password and using `None` the Kuviz will be public
        """

        html = self._get_publication_html(name)
        return self._publisher.update(html, name, password)

    @staticmethod
    def all_publications(credentials=None):
        """Get all map Kuviz published by the current user.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                A Credentials instance. If not provided, the credentials will be automatically
                obtained from the default credentials if available.
        """
        return KuvizPublisher.all(credentials)

    def _get_publication_html(self, name):
        html_map = HTMLMap('templates/viz/main.html.j2')
        html_map.set_content(
            layers=_get_layer_defs(self._publisher.get_layers()),
            bounds=self.bounds,
            size=None,
            camera=self.camera,
            basemap=self.basemap,
            default_legend=self.default_legend,
            show_info=False,
            theme=self.theme,
            title=name,
            description=self.description,
            is_static=self.is_static,
            is_embed=True,
            _carto_vl_path=self._carto_vl_path,
            _airship_path=self._airship_path)

        return html_map.html

    def _validate_default_legend(self, default_legend, title):
        if default_legend and not title:
            raise CartoException('The default legend needs a map title to be displayed')


def _get_publisher(self, credentials):
    return KuvizPublisher(credentials)


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
        'has_legend_list': layer.has_legend_list,
        'widgets': layer.widgets_info,
        'data': layer.source_data,
        'type': layer.source_type,
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
    init_bounds = None
    if layers is not None and len(layers) > 0:
        init_bounds = layers[0].bounds

    bounds = _format_bounds(init_bounds)

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


def _get_theme(theme, basemap):
    if theme and theme not in constants.THEMES:
        raise ValueError(
            'This theme is not valid. Valid themes types are: {}.'.format(
                ', '.join(constants.THEMES)
            ))
    if not theme and basemap == Basemaps.darkmatter:
        return 'dark'

    return theme


def get_token(basemap):
    if isinstance(basemap, dict):
        return get_token(basemap)
    return ''


def get_basecolor(basemap):
    if basemap is None:
        return 'white'
    elif isinstance(basemap, str):
        if basemap not in [Basemaps.voyager, Basemaps.positron, Basemaps.darkmatter]:
            return basemap  # Basemap is a color
    return ''


def get_basemap(basemap):
    if isinstance(basemap, dict):
        token = get_token(basemap)
        if 'style' in basemap:
            if not token and basemap.get('style').startswith('mapbox://'):
                warn('A Mapbox style usually needs a token')
            return basemap.get('style')
        else:
            raise ValueError('If basemap is a dict, it must have a `style` key')
    return ''
