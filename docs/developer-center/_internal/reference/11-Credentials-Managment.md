
Credentials Management[¶](#credentials-management "Permalink to this headline")
-------------------------------------------------------------------------------

Credentials management for cartoframes usage.

_class_ `cartoframes.credentials.``Credentials`(_creds=None_, _key=None_, _username=None_, _base_url=None_, _cred_file=None_)

Credentials class for managing and storing user CARTO credentials. The arguments are listed in order of precedence: [`Credentials`](cartoframes.credentials.html#cartoframes.credentials.Credentials "cartoframes.credentials.Credentials") instances are first, key and base_url/username are taken next, and config_file (if given) is taken last. If no arguments are passed, then there will be an attempt to retrieve credentials from a previously saved session. One of the above scenarios needs to be met to successfully instantiate a [`Credentials`](cartoframes.credentials.html#cartoframes.credentials.Credentials "cartoframes.credentials.Credentials") object.



Parameters:

*   **creds** (`cartoframes.Credentials`, optional) – Credentials instance
*   **key** (_str__,_ _optional_) – API key of user’s CARTO account
*   **username** (_str__,_ _optional_) – Username of CARTO account
*   **base_url** (_str__,_ _optional_) – Base URL used for API calls. This is usually of the form https://eschbacher.carto.com/ for user eschbacher. On premises installations (and others) have a different URL pattern.
*   **cred_file** (_str__,_ _optional_) – Pull credentials from a stored file. If this and all other args are not entered, Credentials will attempt to load a user config credentials file that was previously set with Credentials(…).save().

Raises:

`RuntimeError` – If not enough credential information is passed and no stored credentials file is found, this error will be raised.

Example

from cartoframes import Credentials, CartoContext
creds = Credentials(key='abcdefg', username='eschbacher')
cc = CartoContext(creds=creds)

`base_url`(_base_url=None_)

Return or set base_url.



Parameters:

**base_url** (_str__,_ _optional_) – If set, updates the base_url. Otherwise returns current base_url.

Note

This does not update the username attribute. Separately update the username with `Credentials.username` or update base_url and username at the same time with `Credentials.set`.

Example

>>\> from cartoframes import Credentials
\# load credentials saved in previous session
>>\> creds = Credentials()
\# returns current base_url
>>\> creds.base_url()
'https://eschbacher.carto.com/'
\# updates base_url with new value
>>\> creds.base_url('new\_base\_url')

`delete`(_config_file=None_)

Deletes the credentials file specified in config_file. If no file is specified, it deletes the default user credential file.



Parameters:

**config_file** (_str_) – Path to configuration file. Defaults to delete the user default location if None.

Tip

To see if there is a default user credential file stored, do the following:

>>\> creds = Credentials()
>>\> print(creds)
Credentials(username=eschbacher, key=abcdefg,
 base_url=https://eschbacher.carto.com/)

`key`(_key=None_)

Return or set API key.



Parameters:

**key** (_str__,_ _optional_) – If set, updates the API key, otherwise returns current API key.

Example

>>\> from cartoframes import Credentials
\# load credentials saved in previous session
>>\> creds = Credentials()
\# returns current API key
>>\> creds.key()
'abcdefg'
\# updates API key with new value
>>\> creds.key('new\_api\_key')

`save`(_config_loc=None_)

Saves current user credentials to user directory.



Parameters:

**config_loc** (_str__,_ _optional_) – Location where credentials are to be stored. If no argument is provided, it will be send to the default location.

Example

from cartoframes import Credentials
creds = Credentials(username='eschbacher', key='abcdefg')
creds.save()  \# save to default location

`set`(_key=None_, _username=None_, _base_url=None_)

Update the credentials of a Credentials instance instead with new values.



Parameters:

*   **key** (_str_) – API key of user account. Defaults to previous value if not specified.
*   **username** (_str_) – User name of account. This parameter is optional if base_url is not specified, but defaults to the previous value if not set.
*   **base_url** (_str_) – Base URL of user account. This parameter is optional if username is specified and on CARTO’s cloud-based account. Generally of the form `https://your_user_name.carto.com/` for cloud-based accounts. If on-prem or otherwise, contact your admin.

Example

from cartoframes import Credentials
\# load credentials saved in previous session
creds = Credentials()
\# set new API key
creds.set(key='new\_api\_key')
\# save new creds to default user config directory
creds.save()

Note

If the username is specified but the base_url is not, the base_url will be updated to `https://<username>.carto.com/`.

`username`(_username=None_)

Return or set username.



Parameters:

**username** (_str__,_ _optional_) – If set, updates the username. Otherwise returns current username.

Note

This does not update the base_url attribute. Use Credentials.set to have that updated with username.

Example

>>\> from cartoframes import Credentials
\# load credentials saved in previous session
>>\> creds = Credentials()
\# returns current username
>>\> creds.username()
'eschbacher'
\# updates username with new value
>>\> creds.username('new_username')kkkkkkkkkkkkk
