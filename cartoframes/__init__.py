from .context import CartoContext
from .context import CartoContext as Context
from .credentials import Credentials
from .layer import BaseMap, QueryLayer, Layer
from .styling import BinMethod
from .datasets import Dataset, set_default_context
from .__version__ import __version__

__all__ = [

    # Current API
    'CartoContext',
    'Credentials',
    'BaseMap',
    'QueryLayer',
    'Layer',
    'BinMethod',

    # New API
    'Dataset',
    'Context',
    'set_default_context',

    '__version__'
]
