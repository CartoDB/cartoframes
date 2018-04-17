### CARTO Credential Management

#### Typical usage

The most common way to input credentials into cartoframes is through the CartoContext, as below. Replace {your\_user\_name} with your CARTO username and {your\_api\_key} with your API key, which you can find at `http://{your\_user\_name}.carto.com/your\_apps`.

```python
from cartoframes import CartoContext
cc = CartoContext(
    base_url='https://{your_user_name}.carto.com',
    api_key='{your_api_key}'
)
```

You can also set your credentials using the Credentials class:

```python
from cartoframes import Credentials, CartoContext
cc = CartoContext(
    creds=Credentials(key='{your_api_key}', username='{your_user_name}')
)
```

#### Save/update credentials for later use[¶](#save-update-credentials-for-later-use "Permalink to this headline")

```python
from cartoframes import Credentials, CartoContext
creds = Credentials(username='eschbacher', key='abcdefg')
creds.save()  # save credentials for later use (not dependent on Python session)
```

Once you save your credentials, you can get started in future sessions more quickly:

```python
from cartoframes import CartoContext
cc = CartoContext()  # automatically loads credentials if previously saved
```
