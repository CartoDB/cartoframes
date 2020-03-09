"""Auth namespace contains the class to manage authentication:
:class:`cartoframes.auth.Credentials`.
It also includes the utility functions
:func:`cartoframes.auth.set_default_credentials` and
:func:`cartoframes.auth.get_default_credentials`."""

from .credentials import Credentials
from .defaults import get_default_credentials, set_default_credentials, unset_default_credentials

__all__ = [
    'Credentials',
    'set_default_credentials',
    'get_default_credentials',
    'unset_default_credentials'
]
