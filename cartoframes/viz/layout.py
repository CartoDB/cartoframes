from carto.exceptions import CartoException

from .map import Map
from .html.HTMLLayout import HTMLLayout
from . import constants
from ..utils.utils import get_center


class Layout(object):
    """Create a layout of visualizations in order to compare them.

    Args:
        maps (list of :py:class:`Map <cartoframes.viz.Map>`): List of
          maps. Zero or more of :py:class:`Map <cartoframes.viz.Map>`.
        N_SIZE (number, optional): Number of columns of the layout
        M_SIZE (number, optional): Number of rows of the layout
        viewport (dict, optional): Properties for display of the maps viewport.
          Keys can be `bearing` or `pitch`.

    Examples:

        Basic usage.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer, Layout

            set_default_credentials('your_account')

            Layout([
                Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account')),
                Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account'))
            ])

        Display a 2x2 layout.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer, Layout

            set_default_credentials('your_account')

            Layout([
                Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account')),
                Map(Layer('table_in_your_account')), Map(Layer('table_in_your_account'))
            ], 2, 2)

        Custom Titles.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer, Layout

            set_default_credentials('your_account')

            Layout([
                Map(Layer('table_in_your_account'), title="Visualization 1 custom title"),
                Map(Layer('table_in_your_account'), title="Visualization 2 custom title")),
            ])

        Viewport.

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer, Layout

            set_default_credentials('your_account')

            Layout([
                Map(Layer('table_in_your_account')),
                Map(Layer('table_in_your_account')),
                Map(Layer('table_in_your_account')),
                Map(Layer('table_in_your_account'))
            ], viewport={ 'zoom': 2 })

        .. code::

            from cartoframes.auth import set_default_credentials
            from cartoframes.viz import Map, Layer, Layout

            set_default_credentials('your_account')

            Layout([
                Map(Layer('table_in_your_account'), viewport={ 'zoom': 0.5 }),
                Map(Layer('table_in_your_account')),
                Map(Layer('table_in_your_account')),
                Map(Layer('table_in_your_account'))
            ], viewport={ 'zoom': 2 })
    """

    def __init__(self,
                 maps,
                 N_SIZE=None,
                 M_SIZE=None,
                 viewport=None,
                 map_height=250,
                 is_static=True):
        self._layout = _init_layout(maps, is_static, viewport)
        self._N_SIZE = N_SIZE if N_SIZE is not None else len(self._layout)
        self._M_SIZE = M_SIZE if M_SIZE is not None else constants.DEFAULT_LAYOUT_M_SIZE
        self._viewport = viewport
        self._is_static = is_static
        self._map_height = map_height

    def _repr_html_(self):
        self._htmlLayout = HTMLLayout()
        self._htmlLayout.set_content(
            maps=self._layout,
            size=['100%', self._map_height * self._M_SIZE],
            n=self._N_SIZE,
            m=self._M_SIZE,
            is_static=self._is_static,
            map_height=self._map_height
        )

        return self._htmlLayout.html


def _init_layout(maps, is_static, viewport):
    layout = []

    for i, viz in enumerate(maps):
        if not isinstance(viz, Map):
            raise CartoException('All the elements in the Layout should be an instance of Map')
        else:
            map_settings = _get_map_settings(viz, is_static, viewport)
            layout.append(map_settings)

    return layout


def _get_map_settings(viz, is_static, viewport):
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
