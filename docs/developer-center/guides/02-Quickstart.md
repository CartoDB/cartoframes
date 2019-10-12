## Quickstart

### About this Guide

This guide walks through the process of authenticating CARTOframes to create an interactive visualization with a shareable link. The full notebook example can be found in the [01_basic_usage](https://github.com/CartoDB/cartoframes/blob/develop/examples/01_quickstart/01_basic_usage.ipynb) notebook.

![Final visualization](../../img/guides/quickstart/quickstart-final.gif)

### Install CARTOframes

If you don't have CARTOframes installed, check out the installation steps [here](../../guides/03-Install-CARTOframes-in-your-Notebooks.md) to get started.

### Authentication

If you don't have a CARTO account but want to try out CARTOframes, you only need the `cartoframes` library. To learn more, take a look at the [Data Workflow](LINK) examples to visualize data from either a DataFrame or a GeoJSON.

If you have a CARTO account that you want to use with CARTOframes, you need to authenticate it by passing in your CARTO credentials. You will need your username (`username`) and an API key (`api_key`), which can be found at http://your_user_name.carto.com/your_apps. When using a CARTO account, the elements you need to authenticate are under the `cartoframes.auth` namespace. 

For this guide, we'll use a public dataset from the `cartoframes` account called [`spend_data`](https://cartoframes.carto.com/tables/spend_data/public/map) that contains information about customer spending activities in the city of Barcelona .

```py
from cartoframes.auth import set_default_credentials
from cartoframes.viz import Map, Layer

set_default_credentials(
    username='cartoframes',
    api_key='default_public'
)

Map(Layer('spend_data'))
```

![Visualize the 'spend_data' dataset](../../img/guides/quickstart/quickstart-1.png)

### Change the Viewport and Basemap

By default, the map's center and zoom is set to encompass the entire dataset and visualized on CARTO's Positron basemap. For this map, let's modify these settings to use CARTO's Dark Matter basemap and adjust the viewport to better suite our area of interest:

```py
from cartoframes.viz import Map, Layer, basemaps

Map(
    Layer('spend_data'),
    viewport={'zoom': 12, 'lat': 41.38, 'lng': 2.17},
    basemap=basemaps.darkmatter,
    show_info=True
)
```

### Apply a SQL Query to the Layer

Next, let's filter the data to only show the features where the purchase amount is between 150€ and 200€ using a simple SQL Query:

```py
Map(
    Layer('SELECT * FROM spend_data WHERE amount > 150 AND amount < 200'),
    viewport={'zoom': 12, 'lat': 41.38, 'lng': 2.17},
    basemap=basemaps.darkmatter
)
```

![Apply a simple SQL Query](../../img/guides/quickstart/quickstart-2.png)

## Styles, Legends and Popups

There are two ways to change a layer's style and add legends, popups and widgets: manually (provides greater customization) or with visualization helpers.

First, let's take a look at how to add each element manually and in the next section, we will use a visualization helper to create a similar map.

### Change the Style

To manually overwrite the default color and size of features, you can use the [CARTO VL String API](https://carto.com/developers/carto-vl/guides/style-with-expressions/). This API is very powerful because it allows you to style your visualizations with a few lines of code.

The style can be set directly as the **second** parameter of a Layer.

```py
Map(
    Layer(
        'SELECT * FROM spend_data WHERE amount > 150 AND amount < 200',
        'color: ramp(top($category_en,10), bold)'
    ),
    viewport={'zoom': 12, 'lat': 41.38, 'lng': 2.17},
    basemap=basemaps.darkmatter
)
```

![Style by $category](../../img/guides/quickstart/quickstart-3.png)

### Add a Legend

In this case, the **third** parameter of a Layer is the Legend:

```py
from cartoframes.viz import Legend

Map(
    Layer(
        'SELECT * FROM spend_data WHERE amount > 150 AND amount < 200',
        'color: ramp($category, bold)',
        legend=Legend(
            'color-bins',
            title= 'Categories'
        )
    ),
    viewport={'zoom': 12, 'lat': 41.38, 'lng': 2.17},
    basemap=basemaps.darkmatter
)
```

![Add a legend for the styled category](../../img/guides/quickstart/quickstart-4.png)

### Add a Popup

Now, let's add the Popup settings in the **fourth** parameter:

```py
from cartoframes.viz import Popup

Map(
    Layer(
        'SELECT * FROM spend_data WHERE amount > 150 AND amount < 200',
        'color: ramp(top($category_en,10), bold)',
        legend=Legend(
            'color-bins',
            title= 'Spending Categories'
        ),
        popup=Popup({
            'hover': [{
                'title': 'Day of Week',
                'value': '$weekday'
            },{
                'title': 'Time of Day',
                'value': '$daytime'
            }]
        })
    ),
    viewport={'zoom': 12, 'lat': 41.38, 'lng': 2.17},
    basemap=basemaps.darkmatter
)
```

![Show popups when interacting with the features](../../img/guides/quickstart/quickstart-5.png)

### Add a Widget

Next, let's add a Widget in the **fifth** parameter:

```py
Map(
    Layer(
        'SELECT * FROM spend_data WHERE amount > 150 AND amount < 200',
        'color: ramp(top($category_en,10), bold)',
        legend=Legend(
            'color-bins',
            title= 'Spending Categories'
        ),
        popup=Popup({
            'hover': [{
                'title': 'Day of Week',
                'value': '$weekday'
            },{
                'title': 'Time of Day',
                'value': '$daytime'
            }]
        }),
        widgets=[
            histogram_widget(
                'amount',
                title='Amount Spent (€)',
                description='Select a range of values to filter'
            )
        ]
    ),
    viewport={'zoom': 12, 'lat': 41.38, 'lng': 2.17},
    basemap=basemaps.darkmatter
)
```
And now you have an interactive visualization!

![Final interactive visualization](../../img/guides/quickstart/quickstart-4.png)

## Use a Visualization Helper

In the steps above, you saw how to add each component to a map manually which gives you greater flexibility in customizing the individual pieces of your map.

Next, let's take a look at creating a similar map using the `color_category_layer` which is one of the built-in [Visualization Helpers](LINK TO EXAMPLES) available in CARTOframes. Using a helper, you can quickly create a visualization with default styles,legends, popups, and widgets all together!

```py
from cartoframes.viz.helpers import color_category_layer

Map(
    color_category_layer(
        'SELECT * FROM spend_data WHERE amount > 150 AND amount < 200',
        'category_en',
        'Spending in Barcelona',
        description='Categories',
        widget=True
    ),
    viewport={'zoom': 12, 'lat': 41.38, 'lng': 2.17},
    basemap=basemaps.darkmatter
)
```

![Final visualization](../../img/guides/quickstart/quickstart-final.gif)

## Publish and Share

Once you have a complete visualization, you can publish it and share the output URL!

```py
visualization = Map(
    color_category_layer(
        'SELECT * FROM spend_data WHERE amount > 150 AND amount < 200',
        'category_en', 
        'Spending in Barcelona',
        description='Categories',
        widget=True
    ),
    viewport={'zoom': 12, 'lat': 41.38, 'lng': 2.17},
    basemap=basemaps.darkmatter
)

kuviz = visualization.publish('spending_in_barcelona')

print(kuviz['url'])
```