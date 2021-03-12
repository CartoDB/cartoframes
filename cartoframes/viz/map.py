import collections
import numpy as np

from warnings import warn

from . import constants
from .html import HTMLMap
from .basemaps import Basemaps
from .kuviz import KuvizPublisher
from ..utils.utils import get_center, get_credentials
from ..utils.metrics import send_metrics

WORLD_BOUNDS = [[-180, -90], [180, 90]]


class Map:
    """Map to display a data visualization. It must contain a one or multiple :py:class:`Map <cartoframes.viz.Layer>`
    instances. It provides control of the basemap, bounds and properties of the visualization.

    Args:
        layers (list of :py:class:`Layer <cartoframes.viz.Layer>`): List of
            layers. Zero or more of :py:class:`Layer <cartoframes.viz.Layer>`.
        basemap (str, optional):
            - if a `str`, name of a CARTO vector basemap. One of `positron`,
                `voyager`, or `darkmatter` from the :obj:`BaseMaps` class, or a
                hex, rgb or named color value.
            - if a `dict`, Mapbox or other style as the value of the `style` key.
                If a Mapbox style, the access token is the value of the `token` key.
        bounds (dict or list, optional): a dict with `west`, `south`, `east`, `north`
            keys, or an array of floats in the following structure: [[west,
            south], [east, north]]. If not provided the bounds will be automatically
            calculated to fit all features.
        size (tuple, optional): a (width, height) pair for the size of the map.
          Default is (1024, 632).
        viewport (dict, optional): Properties for display of the map viewport.
          Keys can be `bearing` or `pitch`.
        show_info (bool, optional): Whether to display center and zoom information in the
          map or not. It is False by default.
        is_static (bool, optional): Default False. If True, instead of showing and interactive
          map, a png image will be displayed. Warning: UI components are not properly rendered in
          the static view, we recommend to remove legends and widgets before rendering a static map.
        theme (string, optional): Use a different UI theme (legends, widgets, popups). Available
          themes are `dark` and `ligth`. By default, it is `light` for `Positron` and `Voyager`
          basemaps and `dark` for `DarkMatter` basemap.
        title (string, optional): Title to label the map. and will be displayed in the
          default legend.
        description (string, optional): Text that describes the map and will be displayed in the
          default legend after the title.

    Raises:
        ValueError: if input parameters are not valid.

    Examples:
        Basic usage.

        >>> Map(Layer('table in your account'))

        Display more than one layer on a map.

        >>> Map(layers=[
        ...     Layer('table1'),
        ...     Layer('table2')
        >>> ])

        Change the CARTO basemap style.

        >>> Map(Layer('table in your account'), basemap=basemaps.darkmatter)

        Choose a custom basemap style. Here we use the Mapbox streets style,
        which requires an access token.

        >>> basemap = {
        ...     'style': 'mapbox://styles/mapbox/streets-v9',
        ...     'token': 'your Mapbox token'
        >>> }

        >>> Map(Layer('table in your account'), basemap=basemap)

        Remove basemap and show a custom color.

        >>> Map(Layer('table in your account'), basemap='yellow')  # None, False, 'white', 'rgb(255, 255, 0)'

        Set custom bounds.

        >>> bounds = {
        ...     'west': -10,
        ...     'east': 10,
        ...     'north': -10,
        ...     'south': 10
        >>> } # or bounds = [[-10, 10], [10, -10]]
        >>> Map(Layer('table in your account'), bounds=bounds)

        Show the map center and zoom value on the map (lower left-hand corner).

        >>> Map(Layer('table in your account'), show_info=True)

    """
    def __init__(self,
                 layers=None,
                 basemap=Basemaps.positron,
                 bounds=None,
                 size=None,
                 viewport=None,
                 show_info=None,
                 theme=None,
                 title=None,
                 description=None,
                 is_static=None,
                 layer_selector=False,
                 **kwargs):

        self.layer_selector = layer_selector
        self.basemap = basemap
        self.size = size
        self.viewport = viewport
        self.title = title
        self.description = description
        self.show_info = show_info
        self.is_static = is_static
        self.layers = _init_layers(layers, self)
        self.bounds = _get_bounds(bounds, self.layers)
        self.theme = _get_theme(theme, basemap)

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

    @send_metrics('map_created')
    def _repr_html_(self):
        self._html_map = HTMLMap()

        self._html_map.set_content(
            layers=_get_layer_defs(self.layers),
            bounds=self.bounds,
            size=self.size,
            camera=self.camera,
            basemap=self.basemap,
            show_info=self.show_info,
            theme=self.theme,
            title=self.title,
            description=self.description,
            is_static=self.is_static,
            layer_selector=self.layer_selector,
            _carto_vl_path=self._carto_vl_path,
            _airship_path=self._airship_path)

        return self._html_map.html

    def get_content(self):
        layer_defs = _get_layer_defs(self.layers)

        has_legends = any(layer['legends'] for layer in layer_defs)
        has_widgets = any(len(layer['widgets']) != 0 for layer in layer_defs)

        return {
            'layers': layer_defs,
            'bounds': self.bounds,
            'size': self.size,
            'viewport': self.viewport,
            'camera': self.camera,
            'basemap': self.basemap,
            'basecolor': self.basecolor,
            'token': self.token,
            'show_info': self.show_info,
            'has_legends': has_legends,
            'has_widgets': has_widgets,
            'theme': self.theme,
            'title': self.title,
            'description': self.description,
            'is_static': self.is_static,
            'layer_selector': self.layer_selector,
            '_carto_vl_path': self._carto_vl_path,
            '_airship_path': self._airship_path
        }

    @send_metrics('map_published')
    def publish(self, name, password, credentials=None, if_exists='fail', maps_api_key=None):
        """Publish the map visualization as a CARTO custom visualization.

        Args:
            name (str): The visualization name on CARTO.
            password (str): By setting it, your visualization will be protected by
                password. When someone tries to show the visualization, the password
                will be requested. To disable password you must set it to None.
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                A Credentials instance. If not provided, the credentials will be automatically
                obtained from the default credentials if available. It is used to create the
                publication and also to save local data (if exists) into your CARTO account.
            if_exists (str, optional): 'fail' or 'replace'. Behavior in case a publication with
                the same name already exists in your account. Default is 'fail'.
            maps_api_key (str, optional): The Maps API key used for private datasets.

        Example:
            Publishing the map visualization.

            >>> tmap = Map(Layer('tablename'))
            >>> tmap.publish('Custom Map Title', password=None)

        """
        _credentials = get_credentials(credentials)

        self._publisher = _get_publisher(_credentials)
        self._publisher.set_layers(self.layers, maps_api_key)

        html = self._get_publication_html(name)
        return self._publisher.publish(html, name, password, if_exists)

    def update_publication(self, name, password, if_exists='fail'):
        """Update the published map visualization.

        Args:
            name (str): The visualization name on CARTO.
            password (str): setting it your visualization will be protected by
                password and using `None` the visualization will be public.
            if_exists (str, optional): 'fail' or 'replace'. Behavior in case a publication with the same name already
                exists in your account. Default is 'fail'.

        Raises:
            PublishError: if the map has not been published yet.

        """
        html = self._get_publication_html(name)
        return self._publisher.update(html, name, password, if_exists)

    def _get_publication_html(self, name):
        html_map = HTMLMap('templates/viz/main.html.j2')
        html_map.set_content(
            layers=_get_layer_defs(self._publisher.get_layers()),
            bounds=self.bounds,
            size=None,
            camera=self.camera,
            basemap=self.basemap,
            show_info=False,
            theme=self.theme,
            title=name,
            description=self.description,
            is_static=self.is_static,
            is_embed=True,
            layer_selector=self.layer_selector,
            _carto_vl_path=self._carto_vl_path,
            _airship_path=self._airship_path)

        return html_map.html


def _get_publisher(credentials):
    return KuvizPublisher(credentials)


def _get_bounds(bounds, layers):
    if bounds:
        return _format_bounds(bounds)
    else:
        return _compute_bounds(layers)


def _init_layers(layers, parent_map):
    if layers is None:
        return []
    if not isinstance(layers, collections.abc.Iterable):
        layers.reset_ui(parent_map)
        return [layers]
    else:
        for layer in layers:
            layer.reset_ui(parent_map)
        return layers


def _get_layer_defs(layers):
    if layers is None:
        return None
    return list(map(_get_layer_def, layers))


def _get_layer_def(layer):
    return layer.get_layer_def()


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
        if 'token' in basemap:
            return basemap.get('token')
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
