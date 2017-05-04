"""API key utility functions
"""
import os
import json
import warnings


_FILEPATH = os.path.dirname(os.path.abspath(__file__))
_TARGETPATH = os.path.join(_FILEPATH, 'CARTOCREDS.json')

def set_credentials(url='', api_key='', overwrite=False):
    """Save the CARTO access url and api key so that users can access it via 
    cartoframes.keys.credentials(). This lets users bind their CARTO access
    credentials to a given installation.

    Args:
        url (str): CARTO access URL. Defaults to ''.
        api_key (str): CARTO api key. Defaults to ''.
        overwrite (bool): Whether to overwrite the existing credentials. Defaults to False.
    Returns:
        str: Path to the location of the API key file. Raises EnvironmentError 
             if overwriting is prohibited and the file exists.
    """
    __ = _check_overwrite('url', overwrite)
    stored = _check_overwrite('api_key', overwrite)
    stored['url'] = url
    stored['api_key'] = api_key
    with open(_TARGETPATH, 'w') as outfile:
        json.dump(stored, outfile)
    return _TARGETPATH

def set_url(url, overwrite=False):
    """Save the CARTO access url so that users can access it via 
    cartoframes.keys.acccess_url(). This lets users bind their access url
    to a given installation.

    Args:
        url (str): CARTO access URL
        overwrite (bool): Whether to overwrite the existing key. Defaults to False.

    Returns:
        str: Path to location of the credentials file. Raises FileError if 
             overwriting is prohibited and the file exists.
    """ 
    stored = _check_overwrite('url', overwrite)
    stored['url'] = url
    with open(_TARGETPATH, 'w') as outfile:
        json.dump(stored, outfile)
    return _TARGETPATH

def set_api_key(key, overwrite=False):
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
    stored = _check_overwrite('api_key', overwrite)
    stored['api_key'] = key
    with open(_TARGETPATH, 'w') as outfile:
        json.dump(stored, outfile)
    return _TARGETPATH

def api_key():
    """Returns stored API key that was set with `cartoframes.keys.set_key`

    Returns:
        str: CARTO API key
    """
    return _load_api_key()

def url():
    """Returns stored url that was set with `cartoframes.keys.set_url`

    Returns:
        str: CARTO API url access link
    """
    return _load_url()

def credentials():
    """
    Returns stored credentials that was set with `cartoframes.keys.set_credentials`

    Returns:
        dict:   dictionary containing CARTO url access link and api key.
    """

    return _load_creds()

def _load_creds():
    """Load both URL and api_key from the credentials file

    Args:
        None

    Returns:
            dict: Dictionary containing keys `url` and `api_key`, values are strings. 
            If the credential is not set, the value may be the empty string. 
    """
    try:
        with open(_TARGETPATH, 'r') as f:
            creds = json.load(f)
    except EnvironmentError:
        raise EnvironmentError('No credentials are stored with this installation.'
                               ' Set credentials for this installation using '
                               ' `cartoframes.keys.set_credentials`')

    return dict(url=creds['url'].strip(), api_key=creds['api_key'].strip())

def _load_api_key():
    """Load api_key from the credentials file

    Args:
        None

    Returns:
        str: The api key for the site. If the credential is not set, the string
        may be an empty string.
    """
    return _load_creds()['api_key']

def _load_url():
    """Load url from the credentials file

    Args:
        None

    Returns:
        str: The url for the site installation. If the credential is not set, the string
        may be an empty string.
    """
    return _load_creds()['url']

def _remove_creds():
    """Remove the credential file.

    Args:
        None

    Returns:
        None. Deletes the credential file in place.
    """
    try:
        os.remove(_TARGETPATH)
    except EnvironmentError:
        warnings.warn('No credential file found')

def _clear_attribute(name):
    """Unsets an arbitrary attribute from the credential file.
    
    Args:
        name (str): name of the credential to remove from the credential file

    Returns:
        None. Clears the credential to an empty string in place. 
    """
    with open(_TARGETPATH, 'r') as f:
        creds = json.load(f)
    if name not in creds.keys():
        raise KeyError('{} not found in stored credentials'.format(name))
    creds[name] = ''
    with open(_TARGETPATH, 'w') as f:
        json.dump(creds, f)

def _clear_url():
    """Unsets the url attribute of the credential file
    
    Args:
        None

    Returns:
        None. Clears the credential to an empty string in place. 
    """
    return _clear_attribute('url')

def _clear_api_key():
    """Unsets the api_key attribute of the credential file
    
    Args:
        None

    Returns:
        None. Clears the credential to an empty string in place. 
    """
    return _clear_attribute('api_key')

def _check_overwrite(attribute, overwrite, path=_TARGETPATH):
    """Checks if an attribute is present in the credential file. If it is present
    and the overwrite flag is not set, raises an EnvironmentError. Otherwise, returns
    the stored credentials.

    Args:
        attribute (str): The name of the attribute in the credential file to verify
        overwrite (bool): A flag denoting whether overwriting a set attribute is allowed.
                          If False and the attribute is not empty, a TypeError is raised.
        path (str): The path to the credential file. 

    Returns:
        the dictionary of stored site credentials
    """
    if os.path.isfile(_TARGETPATH):
        with open(_TARGETPATH, 'r') as infile:
            stored = json.load(infile)
        if stored[attribute] != '' and not overwrite:
            raise TypeError('CARTO {} already set and overwrite flag is '
                            'not set'.format(attribute))
        return stored
    else:
        return dict(api_key='', url='')
