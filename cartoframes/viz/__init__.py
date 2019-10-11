"""Viz namespace contains all the classes to create a visualization, mainly
Map and Layer. It also includes our basemaps and the helper methods."""
from __future__ import absolute_import

from .basemaps import Basemaps
from .basemaps import Basemaps as basemaps
from .themes import Themes
from .themes import Themes as themes
from .map import Map
from .layout import Layout
from .layer import Layer
from .source import Source
from .style import Style
from .popup import Popup
from .legend import Legend
from .legend_list import LegendList
from .widget import Widget
from .widget_list import WidgetList

__all__ = [
    'basemaps',
    'Basemaps',
    'themes',
    'Themes',
    'Map',
    'Layout',
    'Layer',
    'Source',
    'Style',
    'Popup',
    'Legend',
    'LegendList',
    'Widget',
    'WidgetList'
]
