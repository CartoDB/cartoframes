import os
import six
import warnings

if not six.PY3:
    FileNotFoundError = OSError 

def set_sitekey(sitekey, overwrite=False):
    """
    Save the sitekey so that users can access it via cenpy.SITEKEY. 
    This lets users bind an API key to a given installation. 

    Arguments
    -----------
    sitekey     :   string
                    string containing the census data api key the user wants to bind
    overwrite   :   bool
                    flag denoting whether to overwrite existing sitekey. Defaults to False. 

    Returns
    --------
    path to the location of the sitekey file or raises FileError if overwriting is prohibited and the file exists.  
    """
    thispath = os.path.dirname(os.path.abspath(__file__))
    targetpath = os.path.join(thispath, 'SITEKEY.txt')
    if os.path.isfile(targetpath):
        if not overwrite:
            raise ValueError('SITEKEY already bound and overwrite flag is not set')
    with open(targetpath, 'w') as outfile:
        outfile.write(sitekey)
    return targetpath

def APIKEY():
    return _load_sitekey()

def _load_sitekey():
    basepath = os.path.dirname(os.path.abspath(__file__))
    targetpath = os.path.join(basepath, 'SITEKEY.txt')
    try:
        with open(targetpath, 'r') as f:
            s = f.read()
        return s.strip()
    except FileNotFoundError:
        return None

def _clear_sitekey():
    basepath = os.path.dirname(os.path.abspath(__file__))
    targetpath = os.path.join(basepath, 'SITEKEY.txt')
    try:
        os.remove(targetpath)
    except FileNotFoundError:
        from warnings import warn
        warn('No site key found!')
