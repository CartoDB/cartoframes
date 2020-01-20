"""
Widget helpers to generate widgets faster.
"""

from .basic_widget import basic_widget
from .animation_widget import animation_widget
from .category_widget import category_widget
from .formula_widget import formula_widget
from .histogram_widget import histogram_widget
from .time_series_widget import time_series_widget
from .default_widget import default_widget


__all__ = [
    'basic_widget',
    'animation_widget',
    'category_widget',
    'formula_widget',
    'histogram_widget',
    'time_series_widget',
    'default_widget'
]
