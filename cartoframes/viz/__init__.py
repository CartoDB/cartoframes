"""Viz namespace contains all the classes to create a visualization, mainly
Map and Layer. It also includes our basemaps and the helper methods."""
from __future__ import absolute_import

from .basemaps import Basemaps as basemaps
from .layer import Layer
from .layout import Layout
from .legend import Legend
from .legend_list import LegendList
from .map import Map
from .popup import Popup
from .source import Source
from .style import Style
from .themes import Themes as themes
from .widget import Widget
from .widget_list import WidgetList
from .popup_list import PopupList
from .popups import popup_element

__all__ = [
    'basemaps',
    'Layer',
    'Layout',
    'Legend',
    'LegendList',
    'Map',
    'popup_element',
    'Popup',
    'PopupList',
    'Source',
    'Style',
    'themes',
    'Widget',
    'WidgetList'
]
