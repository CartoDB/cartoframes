"""Map helper functions bootstrap the process of creating common types of maps.
These functions save time by giving great out-of-the-box cartography, legends,
and popups. The layer can be further customized using optional overrides."""
from __future__ import absolute_import

from .color_bins_layer import color_bins_layer
from .color_category_layer import color_category_layer
from .color_continuous_layer import color_continuous_layer
from .size_bins_layer import size_bins_layer
from .size_category_layer import size_category_layer
from .size_continuous_layer import size_continuous_layer
from .cluster_size_layer import cluster_size_layer
from .cluster_color_bins_layer import cluster_color_bins_layer
from .cluster_color_continuous_layer import cluster_color_continuous_layer
from .animation_layer import animation_layer


def _inspect(helper):
    import inspect
    lines = inspect.getsource(helper)
    print(lines)


__all__ = [
    'animation_layer',
    'cluster_color_bins_layer',
    'cluster_color_continuous_layer',
    'cluster_size_layer',
    'color_bins_layer',
    'color_category_layer',
    'color_continuous_layer',
    'size_bins_layer',
    'size_category_layer',
    'size_continuous_layer'
]
