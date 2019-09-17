## Widgets - Part 1

In CARTOframes it is possible to to add interactive widgets for viewing your map data. Widgets are added to your visualization and do not modify your original data. They allow you to **explore** your map using filters or adding animations, among others.

We use Airship components for the widget's UI and Airship Bridge to connect the widget behaviour with the map. All the widgets accept the following parameters to display widget information: `title`, `description` and `footer`.

There are a variety of widgets available to embed with your map. Widgets can be standalone, combined inside of one layer, or across multiple layers. There are two ways to add widgets (from `cartoframes.viz.widgets`):

1. Using the `Widget` class and passing a dict
2. Using a widget helper

For simplicity, in this guide we're going to create widgets using helper methods:

```py
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import formula_widget

Map(
    Layer('spend_data',
        widgets=[
            formula_widget('amount', 'avg', title="Avg Amount", description="Some description", footer="data source")
        ]
    )
)
```

The following types of widgets are currently supported:

### Default Widgets

The default widget is a general purpose widget that can be used to provide additional information about your map. 

```py
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import default_widget

Map(
    Layer(
        'seattle_collisions',
        widgets=[
            default_widget(
                title='Road Collisions in 2018',
                description='An analysis of collisions in Seattle, WA',
                footer='Data source: City of Seattle'
            )]
    )
)
```

![Default Widget](../../img/guides/widgets/default-widget.png)

### Formula Widgets

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
    Layer(
        'seattle_collisions',
        widgets=[
            formula_widget(
                'count',
                title='Number of Collisions',
                description='Zoom and/or pan the map to update count',
                footer='collisions in this view'
            )
        ]
    )
)
```

![Formula Viewport Widget](../../img/guides/widgets/formula-viewport-widget.gif)

```py
from cartoframes.viz.widgets import formula_widget

Map(
    Layer(
        'seattle_collisions',
        widgets=[
            formula_widget(
                'pedcount',
                'sum',
                is_global=True,
                title='Total Number of Pedestrians',
                description='involved over all collisions',
                footer='pedestrians'
            )
        ]
    )
)
```

![Formula Global Widget](../../img/guides/widgets/formula-global-widget.gif)

### Category Widgets

These widgets allows you to aggregate the data and create categories. Category widgets group features from string columns into aggregated categories based on their occurence in your current map view with their associated count. As you zoom or pan the map, the category widget updates. By default, you can also select a category to filter your map's data.

```py
from cartoframes.viz.widgets import category_widget

Map(
    Layer(
        'seattle_collisions',
        widgets=[
            category_widget(
                'collisiontype',
                title='Type of Collision',
                description='Select a category to filter',
            )
        ]
    )
)
```

![Category Widget](../../img/guides/widgets/category-widget.gif)

### Histogram Widgets

Histogram widgets display the distribution of a numeric attribute, in buckets, to group ranges of values in your data. By default, you can hover over each bar to see each bucket's values and count, and also filter your map's data within a given range.

```py
from cartoframes.viz.widgets import histogram_widget

Map(
    Layer(
        'seattle_collisions',
        widgets=[
            histogram_widget(
                'vehcount',
                title='Number of Vehicles Involved',
                description='Select a range of values to filter',
                buckets=9
            )
        ]
    )
)
```

![Histogram Widget](../../img/guides/widgets/histogram-widget.gif)
