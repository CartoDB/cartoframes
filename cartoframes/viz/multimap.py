from __future__ import absolute_import

import collections
import numpy as np
from carto.exceptions import CartoException

from . import constants
from .basemaps import Basemaps
from .kuviz import KuvizPublisher, kuviz_to_dict
from .html.HTMLMap import HTMLMultiMap

WORLD_BOUNDS = [[-180, -90], [180, 90]]


class MultiMap(object):
    def __init__(self,
                 maps=[],
                 **kwargs):

        self._htmlMultiMap = HTMLMultiMap()

