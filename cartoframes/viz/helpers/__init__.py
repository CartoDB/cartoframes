from __future__ import absolute_import

from .color_category_layer import color_category_layer
from .color_bins_layer import color_bins_layer
from .color_continuous_layer import color_continuous_layer


def _inspect(helper):
    import inspect
    lines = inspect.getsource(helper)
    print(lines)


__all__ = [
    'color_category_layer',
    'color_bins_layer',
    'color_continuous_layer'
]
