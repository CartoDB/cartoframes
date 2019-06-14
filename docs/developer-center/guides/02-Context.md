## Context

Before we can do anything with CARTOframes, we need to authenticate against a CARTO account by passing in CARTO credentials. You will need your username (`base_url`) and an API key (`api_key`), which can be found at http://your_user_name.carto.com/your_apps.

* `base_url`: which is the URL of your CARTO account (`https://your_user_name.carto.com/`)
* `api_key`: if the dataset is **public**, we can use `default_public`. Otherwise, we need to set the API key.

There are two ways to use our credentials:

1. Setting the same credentials by default, which is called the **Default Context**
2. Creating different contexts and passing them to the Map, Layer or Source we want to create, by using the `Context` class.

The elements needed to create contexts are under the `cartoframes.auth` namespace.

### Default Context

With `set_default_context`, the same context will be used by all the layers and sources by default.

```py
from cartoframes.auth import set_default_context

set_default_context(
    base_url='https://your_user_name.carto.com/',
    api_key='default_public'
)
```

### Layer Context

You can set a `Context` for a `Layer`, and different contexts for different leyers:

```py
from cartoframes.auth import Context
from cartoframes.viz import Map, Layer

visualization = Map(
    Layer(
        'dataset',
        context=Context('https://your_user_name.carto.com/', 'default_public')
    )
)
```

```py
from cartoframes.auth import Context
from cartoframes.viz import Map, Layer

context_a=Context('https://your_user_name_a.carto.com/', 'default_public')
context_b=Context('https://your_user_name_b.carto.com/', 'default_public')

visualization = Map([
    Layer('dataset_a', context=context_a),
    Layer('dataset_b', context=context_b)
])
```

### Source Context

But it's also posible to set a `Context` for a `Source`, and different context for different sources:

```py
from cartoframes.auth import Context
from cartoframes.viz import Map, Layer, Source

visualization = Map(
    Layer(
        Source(
            'dataset',
            Context('https://your_user_name_a.carto.com/', 'default_public')
        )
    )
)
```
