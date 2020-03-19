from . import constants
from .map import Map
from .html import HTMLLayout
from ..utils.utils import get_center, get_credentials
from ..utils.metrics import send_metrics
from .kuviz import KuvizPublisher


class Layout:
    """Create a layout of visualizations in order to compare them.

    Args:
        maps (list of :py:class:`Map <cartoframes.viz.Map>`): List of
            maps. Zero or more of :py:class:`Map <cartoframes.viz.Map>`.
        N_SIZE (number, optional): Number of columns of the layout
        M_SIZE (number, optional): Number of rows of the layout
        viewport (dict, optional): Properties for display of the maps viewport.
            Keys can be `bearing` or `pitch`.
        is_static (boolean, optional): By default, all the maps in each visualization
            are static images due to performance reasons. In order to set them interactive,
            set `is_static` to True.
        map_height (number, optional): Height in pixels for each visualization.
            Default is 250.
        full_height (boolean, optional): When a layout visualization is published, it
            will fit the screen height. Otherwise, each visualization height will be
            `map_height`. Default True.

    Raises:
        ValueError: if the input elements are not instances of :py:class:`Map <cartoframes.viz.Map>`.

    Examples:
        Basic usage.

        >>> Layout([
        ...    Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account')),
        ...    Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account'))
        >>> ])

        Display a 2x2 layout.

        >>> Layout([
        ...     Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account')),
        ...     Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account'))
        >>> ], 2, 2)

        Custom Titles.

        >>> Layout([
        ...     Map(Layer('table_in_your_account'), title="Visualization 1 custom title"),
        ...     Map(Layer('table_in_your_account'), title="Visualization 2 custom title")),
        >>> ])

        Viewport.

        >>> Layout([
        ...     Map(Layer('table_in_your_account')),
        ...     Map(Layer('table_in_your_account')),
        ...     Map(Layer('table_in_your_account')),
        ...     Map(Layer('table_in_your_account'))
        >>> ], viewport={ 'zoom': 2 })

        >>> Layout([
        ...     Map(Layer('table_in_your_account'), viewport={ 'zoom': 0.5 }),
        ...     Map(Layer('table_in_your_account')),
        ...     Map(Layer('table_in_your_account')),
        ...     Map(Layer('table_in_your_account'))
        >>> ], viewport={ 'zoom': 2 })

        Create an interactive layout

        >>> Layout([
        ...    Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account')),
        ...    Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account'))
        >>> ], is_static=False)

    """
    def __init__(self,
                 maps,
                 n_size=None,
                 m_size=None,
                 viewport=None,
                 map_height=250,
                 full_height=True,
                 is_static=True,
                 **kwargs):

        self._maps = maps
        self._layout = _init_layout(self._maps, is_static, viewport)
        self._n_size = n_size if n_size is not None else len(self._layout)
        self._m_size = m_size if m_size is not None else constants.DEFAULT_LAYOUT_M_SIZE
        self._viewport = viewport
        self._is_static = is_static
        self._map_height = map_height
        self._full_height = full_height
        self._publisher = None
        self._carto_vl_path = kwargs.get('_carto_vl_path', None)
        self._airship_path = kwargs.get('_airship_path', None)

    def _repr_html_(self):
        self._html_layout = HTMLLayout()
        map_height = '100%' if self._full_height else '{}px'.format(self._map_height)

        self._html_layout.set_content(
            maps=self._layout,
            size=['100%', self._map_height * self._m_size],
            n_size=self._n_size,
            m_size=self._m_size,
            is_static=self._is_static,
            map_height=map_height,
            full_height=self._full_height,
            _carto_vl_path=self._carto_vl_path,
            _airship_path=self._airship_path
        )

        return self._html_layout.html

    @send_metrics('map_published')
    def publish(self, name, password, credentials=None, if_exists='fail', maps_api_key=None):
        """Publish the layout visualization as a CARTO custom visualization.

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

            >>> tlayout = Layout([
            ...    Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account')),
            ...    Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account'))
            >>> ])

            >>> tlayout.publish('Custom Map Title', password=None)
        """

        _credentials = get_credentials(credentials)
        layers = []

        for viz_map in self._maps:
            for layer in viz_map.layers:
                layers.append(layer)

        self._publisher = _get_publisher(_credentials)
        self._publisher.set_layers(layers, maps_api_key)

        html = self._get_publication_html()
        return self._publisher.publish(html, name, password, if_exists)

    def delete_publication(self):
        """Delete the published layout visualization."""
        return self._publisher.delete()

    def update_publication(self, name, password, if_exists='fail'):
        """Update the published layout visualization.

        Args:
            name (str): The visualization name on CARTO.
            password (str): setting it your visualization will be protected by
                password and using `None` the visualization will be public.
            if_exists (str, optional): 'fail' or 'replace'. Behavior in case a publication with the same name already
                exists in your account. Default is 'fail'.

        Raises:
            PublishError: if the map has not been published yet.

        """
        html = self._get_publication_html()
        return self._publisher.update(html, name, password, if_exists)

    @staticmethod
    def all_publications(credentials=None):
        """Get all map visualization published by the current user.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                A Credentials instance. If not provided, the credentials will be automatically
                obtained from the default credentials if available.

        """
        _credentials = get_credentials(credentials)

        return KuvizPublisher.all(_credentials)

    def _get_publication_html(self):
        if not self._publisher:
            _credentials = get_credentials(None)
            self._publisher = _get_publisher(_credentials)

        html_layout = HTMLLayout('templates/viz/main_layout.html.j2')

        layers = self._publisher.get_layers()

        for viz_map in self._maps:
            viz_map.layer_defs = []

        for layer in layers:
            layer.reset_legends(self._maps[layer.map_index])
            layer_def = layer._get_layer_def()
            self._maps[layer.map_index].layer_defs.append(layer_def)

        maps = _init_layout(self._maps, self._is_static, self._viewport)
        map_height = '100%' if self._full_height else '{}px'.format(self._map_height)

        html_layout.set_content(
            maps=maps,
            size=['100%', self._map_height * self._m_size],
            n_size=self._n_size,
            m_size=self._m_size,
            is_static=self._is_static,
            is_embed=True,
            map_height=map_height
        )

        return html_layout.html


def _init_layout(maps, is_static, viewport):
    layout = []

    for map_index, viz in enumerate(maps):
        if not isinstance(viz, Map):
            raise ValueError('All the elements in the Layout should be an instance of Map.')

        for layer in viz.layers:
            layer.map_index = map_index

        map_settings = _get_map_settings(viz, is_static, viewport, map_index)

        layout.append(map_settings)

    return layout


def _get_map_settings(viz, is_static, viewport, map_index):
    map_settings = viz.get_content()

    map_settings['viewport'] = _get_viewport(map_settings['viewport'], viewport)
    map_settings['camera'] = _get_camera(map_settings['viewport'])
    map_settings['is_static'] = _get_is_static(map_settings['is_static'], is_static)

    return map_settings


def _get_viewport(map_settings_viewport, layout_viewport):
    if map_settings_viewport is not None:
        return map_settings_viewport

    return layout_viewport


def _get_camera(viewport):
    camera = None
    if viewport is not None:
        camera = {
            'center': get_center(viewport),
            'zoom': viewport.get('zoom'),
            'bearing': viewport.get('bearing'),
            'pitch': viewport.get('pitch')
        }
    return camera


def _get_is_static(map_settings_is_static, layout_is_static):
    if map_settings_is_static is not None:
        return map_settings_is_static

    return layout_is_static


def _get_publisher(credentials):
    return KuvizPublisher(credentials)
