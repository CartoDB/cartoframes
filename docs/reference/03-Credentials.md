### CARTO Credential Management

#### Typical usage

The most common way to input credentials into cartoframes is through the CartoContext, as below. Replace {your\_user\_name} with your CARTO username and {your\_api\_key} with your API key, which you can find at `http://{your_user_name}.carto.com/your_apps`.

```python
from cartoframes import CartoContext
cc = CartoContext(
    base_url='https://{your\_user\_name}.carto.com',
    api_key='{your\_api\_key}'
)
```

You can also set your credentials using the Credentials class:

```python
from cartoframes import Credentials, CartoContext
cc = CartoContext(
    creds=Credentials(key='{your\_api\_key}', username='{your\_user\_name}')
)
```

#### Save/update credentials for later use[¶](#save-update-credentials-for-later-use "Permalink to this headline")

```python
from cartoframes import Credentials, CartoContext
creds = Credentials(username='eschbacher', key='abcdefg')
creds.save()  \# save credentials for later use (not dependent on Python session)
```

Once you save your credentials, you can get started in future sessions more quickly:

```python
from cartoframes import CartoContext
cc = CartoContext()  \# automatically loads credentials if previously saved
```
