## Widgets - Part 2

In CARTOframes it is possible to to add interactive widgets for viewing your map data. Widgets are added to your visualization and do not modify your original data. They allow you to **explore** your map using filters or adding animations, among others.

This is the continuation of the [Widgets Part 1]({{ site.url }}/developers/cartoframes/guides/widgets-part-1/)

### Animation Controls Widget

This widget makes possible to control the animation present in the visualization. Only **one** animation can be controled. To add an animation, it is currently needed to understand how to create [Animated visualizations](https://carto.com/developers/carto-vl/guides/animated-visualizations/).

The animation widget will get the animation expression from the `filter` property:

```py
from cartoframes.viz.widgets import animation_widget

Map(
    Layer(
        'seattle_collisions',
        'filter: animation($incdate, 20, fade(0.5,0.5))',
        widgets=[
            animation_widget(
                title='Collision Date',
                description= 'Play, pause, or select the range of the animation'
            )]
    )
)
```

![Animation Widget](../../img/guides/widgets/animation-widget.gif)

### Animation Widget and Style Properties

As mentioned above, the animation widget gets the animation expression from the `filter` property:

```py
from cartoframes.auth import set_default_credentials
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import animation_widget

set_default_credentials('cartovl')

Map(
    Layer(
        'seattle_collisions',
        'filter: animation($incdate, 30, fade(1, 1))',
        widgets=[animation_widget()]
    )
)
```

However, if you want to animate the features by another property, for example, by `width`, you have to provide this information to the widget throught the `prop` parameter:

```py
from cartoframes.auth import set_default_credentials
from cartoframes.viz import Map, Layer
from cartoframes.viz.widgets import animation_widget

set_default_credentials('cartovl')

Map(
    Layer(
        'seattle_collisions',
        'width: animation(linear($incdate), 20,fade(1, 1)) * ramp(linear($personcount, 2, 5), [5, 20])',
        widgets=[animation_widget(prop='width')]
    )
)
```

![Animation by Property Widget](../../img/guides/widgets/animation-property-widget.gif)

### Time-Series Widget

The time series widget enables you to display animated data (by aggregation) over a specified date or numeric field. Time series widgets provide a status bar of the animation, controls to play or pause, and the ability to filter on a range of values.

```py
from cartoframes.viz.widgets import time_series_widget

Map(
    Layer(
        'seattle_collisions',
        'filter: animation($incdate, 20, fade(0.5,0.5))',
        widgets=[
            time_series_widget(
                value='incdate',
                title='Number of Collisions by Date',
                description= 'Play, pause, or select a range for the animation',
                buckets=10
            )]
    )
)
```

![Time Series Widget](../../img/guides/widgets/time-series-widget.gif)

### Combine multiple widgets

It is possible to combine widgets on your map. The map below, uses a formula widget to count the number of pedestrian involved collisions with the address type of where the collision occured. You can filter a category and the formula widget will update to relflect the values of that category in the current map view.

```py
from cartoframes.viz.widgets import category_widget, formula_widget

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
            ),
            category_widget('addrtype')
        ]
    )
)
```

![Combined Widgets](../../img/guides/widgets/combine-widgets.gif)
