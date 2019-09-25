"""
Widget helpers to generate widgets faster.
"""

from __future__ import absolute_import

from .animation_widget import animation_widget
from .category_widget import category_widget
from .default_widget import default_widget
from .formula_widget import formula_widget
from .histogram_widget import histogram_widget
from .time_series_widget import time_series_widget

__all__ = [
    'animation_widget',
    'category_widget',
    'default_widget',
    'formula_widget',
    'histogram_widget',
    'time_series_widget',
]


def _inspect(widget):
    import inspect
    lines = inspect.getsource(widget)
    print(lines)
