"""
.. code::
    from cartoframes import set_default_context
    from cartoframes.examples import example_context
    from cartoframes.vis import Map, Layer

    set_default_context(example_context)

    Map(
        Layer(
            'nat',
            '''
            color: ramp(globalEqIntervals($hr90, 7), sunset)
            strokeWidth:0
            '''
        )
    )
"""

from __future__ import absolute_import

from .basemaps import Basemaps as basemaps
from . import defaults
from .map import Map
from .layer import Layer
from .source import Source
from .style import Style


__all__ = [
    'basemaps',
    'defaults',
    'Map',
    'Layer',
    'Source',
    'Style'
]
