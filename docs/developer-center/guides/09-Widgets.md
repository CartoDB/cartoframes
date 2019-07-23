## Widgets

In CARTOframes it is possible to to add interactive widgets for viewing your map data. Widgets are added to your visualization and do not modify your original data. They allow you to **explore** your map using filters or adding animations, among others.

We use Airship components for the widget's UI and Airship Bridge to connect the widget behaviour with the map. All the widgets accept the following parameters to display widget information: `title`, `description` and `footer`:

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import formula_widget

Map(
    Layer('spend_data',
        widgets=[
            formula_widget('$amount', 'avg', title="Avg Amount", description="Some description", footer="data source")
        ]
    )
)
```

### Widget Types

The following types of widgets are currently supported:

#### Formula Widgets

The Formula Widget calculates aggregated values from numeric columns. The operations supported are: avg, max, min, sum and count. By default, only the data visible in the viewport is used. In order to use all the data in the dataset, it is necessary to set `is_global` to `True`.

- Viewport Count: `formula_widget('count')`
- Global Count: `formula_widget('count', is_global=True)`
- Viewport Average: `formula_widget('$numeric_value', 'avg')`
- Global Average: `formula_widget('$numeric_value', 'avg', is_global=True)`
- Viewport Max: `formula_widget('$numeric_value', 'max')`
- Global Max: `formula_widget('$numeric_value', 'max', is_global=True)`
- Viewport Min: `formula_widget('$numeric_value', 'min')`
- Global Min: `formula_widget('$numeric_value', 'min', is_global=True)`
- Viewport Sum: `formula_widget('$numeric_value', 'sum')`
- Global Sum: `formula_widget('$numeric_value', 'sum', is_global=True)`

```py
from cartoframes.viz.widgets import formula_widget

Map(
    Layer('spend_data',
        widgets=[formula_widget('count', title="Feature Count", is_global=True)]
    )
)
```

#### Histogram Widgets

The Histogram Widget examines numerical values within a given range, distributed across your data map. You can configure values by a data column and define the number of buckets with the `buckets` parameter.

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import histogram_widget

Map(
    Layer('spend_data',
        widgets=[histogram_widget('$amount', title="Amount", footer="data source", buckets=10)]
    )
)
```

#### Category Widgets

These widgets allows you to aggregate the data and create categories.

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import category_widget

Map(
    Layer(
        'spend_data',
        'color: ramp($category, Bold)'
        widgets=category_widget('$category', title="Category", footer="data source")
    )
)
```

#### Animation Controls Widget

This widget makes possible to control the animation present in the visualization. Only **one** animation can be controled. To add an animation, it is currently needed to understand how to create [Animated visualizations](https://carto.com/developers/carto-vl/guides/animated-visualizations/).

The animation widget will get the animation expression from the `filter` property:

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import animation_widget

Map(
    Layer(
        'spend_data',
        'filter: animation($date, 30, fade(1, 1))'
        widgets=animation_widget()
    )
)
```

However, if we want to animate the features by other property, for example, by `width`, we have to provide this information to the widget throught the `prop` parameter:

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import animation_widget

Map(
    Layer(
        'spend_data',
        'width: animation(linear($date), 20,fade(1, 1)) * ramp(linear($amount, 2, 5), [5, 20])'
        widgets=animation_widget(prop='width')
    )
)
```

#### Time-Series Widgets

These widgets enable you to display animated data (by aggregation) over a specified date range, or display and filter a static widget of numbers over time.

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import time_series_widget

Map(
    Layer(
      'spend_data',
        widgets=time_series_widget('$value', buckets=10)
    )
)
```

### Combine multiple widgets

The `widgets` parameter allows a list of widgets. They will be added in the right sidebar from top to bottom. You can interact with the widgets to combine the filters: when selecting a category, the animation filter will be combined with the category filter and will only show the category filtered.

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import animation_widget

Map(
    Layer(
        'spend_data',
        '''
        width: animation(linear($date), 20,fade(1, 1)) * ramp(linear($amount, 2, 5), [5, 20])
        color: ramp($category, Bold)
        '''
        widgets=[
          animation_widget(prop='width'),
          category_widget('$category')
        ]
    )
)
```
