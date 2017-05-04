"""API key utility functions
"""
import os
import warnings

def set_key(key, overwrite=False):
    """Save the CARTO API key so that users can access it via
    cartoframes.keys.api_key(). This lets users bind an API key to a given
    installation.

    Args:
        key (str): CARTO API key
        overwrite (bool): Whether to overwrite existing key. Defaults to False.

    Returns:
        str: Path to the location of the API key file. Raises FileError if
        overwriting is prohibited and the file exists.
    """
    thispath = os.path.dirname(os.path.abspath(__file__))
    targetpath = os.path.join(thispath, 'CARTOKEY.txt')

    if os.path.isfile(targetpath):
        if not overwrite:
            raise ValueError('CARTO API key already set and overwrite flag is '
                             'not set')

    with open(targetpath, 'w') as outfile:
        outfile.write(key)

    return targetpath

def api_key():
    """Returns stored API key that was set with `cartoframes.keys.set_key`

    Returns:
        str: CARTO API key
    """
    return _load_key()

def _load_key():
    basepath = os.path.dirname(os.path.abspath(__file__))
    targetpath = os.path.join(basepath, 'CARTOKEY.txt')
    try:
        with open(targetpath, 'r') as f:
            key = f.read()

        return key.strip()
    except EnvironmentError:
        warnings.warn('No API key found')
        return None

def _clear_key():
    basepath = os.path.dirname(os.path.abspath(__file__))
    targetpath = os.path.join(basepath, 'CARTOKEY.txt')
    try:
        os.remove(targetpath)
    except EnvironmentError:
        warnings.warn('No API key found')
