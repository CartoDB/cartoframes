"""Auth namespace contains the necessary tools to manage authentication by allowing
the user to set its CARTO credentials."""
from __future__ import absolute_import

from .credentials import Credentials
from .defaults import get_default_credentials, set_default_credentials

__all__ = [
    'Credentials',
    'set_default_credentials',
    'get_default_credentials'
]
