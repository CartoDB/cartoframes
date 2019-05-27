from .context import CartoContext
from .context import CartoContext as Context
from .credentials import Credentials
from .layer import BaseMap, QueryLayer, Layer
from .styling import BinMethod
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
    'Context',

    '__version__'
]
