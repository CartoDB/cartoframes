"""
Legend helpers to generate legends faster.
"""

from .basic_legend import basic_legend
from .color_bins_legend import color_bins_legend
from .color_category_legend import color_category_legend
from .color_continuous_legend import color_continuous_legend
from .size_bins_legend import size_bins_legend
from .size_category_legend import size_category_legend
from .size_continuous_legend import size_continuous_legend
from .default_legend import default_legend

__all__ = [
    'basic_legend',
    'color_bins_legend',
    'color_category_legend',
    'color_continuous_legend',
    'size_bins_legend',
    'size_category_legend',
    'size_continuous_legend',
    'default_legend'
]
