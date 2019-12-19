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

from .widgets import basic_widget
from .widgets import animation_widget
from .widgets import category_widget
from .widgets import formula_widget
from .widgets import histogram_widget
from .widgets import time_series_widget

from .legends import basic_legend
from .legends import color_bins_legend
from .legends import color_category_legend
from .legends import color_continuous_legend
from .legends import size_bins_legend
from .legends import size_category_legend
from .legends import size_continuous_legend

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
    'basic_widget',
    'animation_widget',
    'category_widget',
    'formula_widget',
    'histogram_widget',
    'time_series_widget',
    'basic_legend',
    'color_bins_legend',
    'color_category_legend',
    'color_continuous_legend',
    'size_bins_legend',
    'size_category_legend',
    'size_continuous_legend'
]
