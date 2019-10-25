## Login to CARTO Platform

In this guide, our purpose is to focus on the basics of authentication in CARTOframes. There's a full [Authorization Fundamentals](https://carto.com/developers/fundamentals/authorization/) at CARTO guide to understand how to configure and manage API Keys.

> To use CARTOframes is *not always* needed to be authenticated.

It is needed to set up the user credentials to use Data Services or the Data Observatory, between others. In these cases, it's required to have a [CARTO account](https://carto.com/signup/). Once the user has created an account, the credentials can be found at **http://johnsmith.carto.com/your_apps.** for user `johnsmith`, and it should be a **Master** API Key:

![Master API Key - CARTO Dashboard](../../img/guides/credentials/api-keys.png)

All user accounts have a `default_public` API Key to access **public** data.

### Credential parameters

- `username`: your CARTO account username
- `base_url`: Base URL used for API calls. This is usually of the form `https://johnsmith.carto.com/` for user `johnsmith`. On premises installation (and others) have a different URL pattern.
- `api_key`: API Key of user's CARTO account. If the data is to be accessed is **public**, it can be set to `default_public`.

### Default Credentials

With [set_default_credentials](/developers/cartoframes/reference/#cartoframes-auth-set_default_credentials), the same user's authentication will be used by _all_ layers and sources by default.

```py
from cartoframes.auth import set_default_credentials

set_default_credentials(
    username='johnsmith',
    api_key='1a2b3c4d5e6f7g8h'
)
```

Credentials can be also set by using the `base_url` parameter, which is useful when having an **On premise** or a custom installation:

```py
from cartoframes.auth import set_default_credentials

set_default_credentials(
    base_url='https://johnsmith.carto.com/',
    api_key='1a2b3c4d5e6f7g8h'
)
```

When the data is public, the `api_key` parameter isn't required: it's automatically set to `default_public`:

```py
from cartoframes.auth import set_default_credentials

set_default_credentials('johnsmith')
```

### Specific Credentials

Instead of setting credentials generally, it is possible to assign specific and different credentials for a Map, Dataset, Layer or Source, between others.

```py
from cartoframes.auth import Credentials
from cartoframes.data import Dataset

dataset = Dataset('dataset', credentials=Credentials('johnsmith', '1a2b3c4d5e6f7g8h'))
```

### The config file

Credentials can be stored in a **configuration file** with the following format:

Example `config.json` file:

```json
{
  "APIKEY": "",
  "USERNAME": "",
  "USERURL": "https://{username}.carto.com/"
}
```

The filename is `cartocreds.json` by default, but it can be overwriten. There are [different methods](/developers/cartoframes/reference/#cartoframes-auth-Credentials) to read, update and delete your credentials.
