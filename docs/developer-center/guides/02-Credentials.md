## Credentials

When you works using CARTOframes, if you need to connect with your CARTO account (to use your datasets, creating new ones, ...), you first need to authenticate against a CARTO account by passing in CARTO credentials. You will need your username (`username`) and an API key (`api_key`), which can be found at **http://your_user_name.carto.com/your_apps.**

![API Key - CARTO Dashboard](../../img/guides/context/api-keys.png)

* `username`: your CARTO account username
* `api_key`: if the dataset is **public**, you can use `default_public`. Otherwise, you need to set the API key.

There are two ways to use these credentials:

1. Setting the same credentials by default, which is called the **Default Credentials**
2. Creating different credentials instances and passing them to the Map, Layer, Source or Dataset we want to create, by using the `Credentials` class.

The elements needed to create contexts are under the `cartoframes.auth` namespace.

### Default Context

With `set_default_credentials`, the same context will be used by _all_ layers and sources by default.

```py
from cartoframes.auth import set_default_credentials

set_default_credentials(
    username='your_user_name',
    api_key='default_public'
)
```
You can also set your credentials using the base_url parameter:

```py
from cartoframes.auth import set_default_credentials

set_default_credentials(
    base_url='https://your_user_name.carto.com/',
    api_key='default_public'
)
```

When the data we're going to use is public, we don't need the `api_key` parameter, it's automatically set to `default_public`:

```py
from cartoframes.auth import set_default_credentials

set_default_context('your_user_name')
```

### Dataset Credentials

You can set a `Credentials` for a `Dataset` if you are working with data from your CARTO account

```py
from cartoframes.auth import Credentials
from cartoframes.data import Dataset

Dataset('dataset', credentials=Credentials('your_user_name', 'your_api_key'))
```

### Layer Credentials

You can set a `Credentials` for a `Layer`, and different contexts for different layers:

```py
from cartoframes.auth import Credentials
from cartoframes.viz import Map, Layer

visualization = Map(
    Layer(
        'dataset',
        credentials=Credentials('your_user_name', 'your_api_key')
    )
)
```

Or, if it's public:

```py
from cartoframes.auth import Credentials
from cartoframes.viz import Map, Layer

visualization = Map(
    Layer(
        'dataset',
        credentials=Credentials('your_user_name', 'your_api_key')
    )
)
```

Using a different context for each layer:

```py
from cartoframes.auth import Credentials
from cartoframes.viz import Map, Layer

credentials_a=Credentials('your_user_name_a')
credentials_b=Credentials('your_user_name_b')

visualization = Map([
    Layer('dataset_a', credentials=credentials_a),
    Layer('dataset_b', credentials=credentials_b)
])
```

### Source Context

It is also possible to set a `Credentials` for a `Source`, and different contexts for different sources:

```py
from cartoframes.auth import Context
from cartoframes.viz import Map, Layer, Source

visualization = Map(
    Layer(
        Source(
            'dataset',
            Credentials('your_user_name')
        )
    )
)
```
