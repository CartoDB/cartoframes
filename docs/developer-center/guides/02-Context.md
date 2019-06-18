## Context

To get started using CARTOframes, you first need to authenticate against a CARTO account by passing in CARTO credentials. You will need your username (`base_url`) and an API key (`api_key`), which can be found at **http://your_user_name.carto.com/your_apps.**

![API Key - CARTO Dashboard](../../img/guides/context/api-keys.png)

* `base_url`: the URL of your CARTO account (`https://your_user_name.carto.com/`)
* `api_key`: if the dataset is **public**, you can use `default_public`. Otherwise, you need to set the API key.

There are two ways to use these credentials:

1. Setting the same credentials by default, which is called the **Default Context**
2. Creating different contexts and passing them to the Map, Layer or Source we want to create, by using the `Context` class.

The elements needed to create contexts are under the `cartoframes.auth` namespace.

### Default Context

With `set_default_context`, the same context will be used by _all_ layers and sources by default.

```py
from cartoframes.auth import set_default_context

set_default_context(
    base_url='https://your_user_name.carto.com/',
    api_key='default_public'
)
```

When the data we're going to use is public, we don't need the `api_key` parameter, it's automatically set to `default_public`:

```py
from cartoframes.auth import set_default_context

set_default_context('https://your_user_name.carto.com/')
```

### Layer Context

You can set a `Context` for a `Layer`, and different contexts for different leyers:

```py
from cartoframes.auth import Context
from cartoframes.viz import Map, Layer

visualization = Map(
    Layer(
        'dataset',
        context=Context('https://your_user_name.carto.com/', 'your_api_key')
    )
)
```

Or, if it's public:

```py
from cartoframes.auth import Context
from cartoframes.viz import Map, Layer

visualization = Map(
    Layer(
        'dataset',
        context=Context('https://your_user_name.carto.com/')
    )
)
```

Using a different context for each layer:

```py
from cartoframes.auth import Context
from cartoframes.viz import Map, Layer

context_a=Context('https://your_user_name_a.carto.com/')
context_b=Context('https://your_user_name_b.carto.com/')

visualization = Map([
    Layer('dataset_a', context=context_a),
    Layer('dataset_b', context=context_b)
])
```

### Source Context

It is also possible to set a `Context` for a `Source`, and different contexts for different sources:

```py
from cartoframes.auth import Context
from cartoframes.viz import Map, Layer, Source

visualization = Map(
    Layer(
        Source(
            'dataset',
            Context('https://your_user_name_a.carto.com/')
        )
    )
)
```
