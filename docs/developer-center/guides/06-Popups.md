## Popups

**Popups** are useful for interactively displaying additional information about a feature on a map. The events that allow us to interact with the feature are `hover` and `click`. A feature can listen to both events and display different information for each one.

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer

set_default_context('https://cartovl.carto.com/')
```

### Basic popups

```py
Map(
    Layer(
        'sf_neighborhoods',
        'color: ramp(globalQuantiles($cartodb_id, 5), purpor)',
        {
            'hover': '$name',
            'click': ['$name', '$created_at']
        }
    )
)
```

![Set Popup for 'hover' and 'click' events](../../img/guides/popups/popups-1.png)

### Using expressions

```py
Map(
    Layer(
        'populated_places',
        'width: 15',
        {
            'hover': ['sqrt($pop_max)', '$pop_min % 100']
        }
    ),
    viewport={'zoom': 3.89, 'lat': 39.90, 'lng': 5.52}
)
```

![Set Popup for 'hover' events using expressions](../../img/guides/popups/popups-2.png)

### Adding titles

```py
from cartoframes.viz import Popup

Map(
    Layer(
        'sf_neighborhoods',
        popup=Popup({
            'hover': {
                'title': 'Name',
                'value': '$name'
            },
            'click': [{
                'title': 'Name',
                'value': '$name'
            },{
                'title': 'Created at',
                'value': '$created_at'
            }]
        })
    )
)
```

![Set Popup title and value for 'hover' and 'click' events](../../img/guides/popups/popups-3.png)
