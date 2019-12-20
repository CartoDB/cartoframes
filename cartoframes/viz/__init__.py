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

from .styles import color_bins_style
from .styles import color_category_style
from .styles import color_continuous_style
from .styles import size_bins_style
from .styles import size_category_style
from .styles import size_continuous_style

from .widgets import animation_widget
from .widgets import category_widget
from .widgets import default_widget
from .widgets import formula_widget
from .widgets import histogram_widget
from .widgets import time_series_widget

__all__ = [
    'basemaps',
    'themes',
    'Map',
    'Layout',
    'Layer',
    'Source',
    'Style',
    'Popup',
    'Legend',
    'LegendList',
    'Widget',
    'WidgetList',

    'color_bins_style',
    'color_category_style',
    'color_continuous_style',
    'size_bins_style',
    'size_category_style',
    'size_continuous_style',

    'animation_widget',
    'category_widget',
    'default_widget',
    'formula_widget',
    'histogram_widget',
    'time_series_widget'
]
