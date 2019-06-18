## Quickstart

### About this Guide

This guide walks you through the process of installing and authenticating CARTOframes to create an interactive visualization with a shareable link. The full notebook example can be found in the [01_basic_usage](https://github.com/CartoDB/cartoframes/blob/master/examples/01_quickstart/01_basic_usage.ipynb) notebook.

![Final visualization](../../img/guides/quickstart/quickstart-final.gif)

### Install CARTOframes

You can install CARTOframes with `pip`. Simply type the following in the command line to do a system install:

```bash
$ pip install cartoframes
```

To install through a Jupyter notebook, you can run

```bash
!pip install cartoframes
```

It is recommended to install cartoframes in a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/). For example, you can run the following command to create a virtual env, activate it, and install cartoframes:

```bash
$ virtualenv cfenv
$ source cfenv/bin/activate
(cfenv) $ pip install cartoframes
```

You'll notice the virtual environment name in your command line prompt, like above. Type `deactivate` to exit the virtualenv:

```bash
(cfenv) $ deactivate
```

### Install Jupyter notebook

To install Jupyter, type:

```bash
$ pip install jupyter
```

If working in a virtual environment, make sure you have activated the environment first.

### Start the Jupyter notebook

Start up a Jupyter notebook with the following command:

```bash
$ jupyter notebook
```

After you type that command, you will see the notebook server starting up and a browser window with the directory contents open.

Next, create a new notebook. See Jupyter's [running a notebook](https://jupyter.readthedocs.io/en/latest/running.html#running) for more information.

### Authentication

Before you can interact with CARTOframes, you need to authenticate against a CARTO account by passing in CARTO credentials. You will need your username (`base_url`) and an API key (`api_key`), which can be found at http://your_user_name.carto.com/your_apps. 

If you don't have a CARTO account but want to try out CARTOframes, you only need the cartoframes library. To learn more, take a look at the Sources examples to visualize data from either a Dataframe or a GeoJSON.

The elements we need to create contexts are under the `cartoframes.auth` namespace. For this guide, we'll use a public dataset from the `cartoframes` account called [`spend_data`](https://cartoframes.carto.com/tables/spend_data/public/map) that contains information about customer spending activities in the city of Barcelona .

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer

set_default_context(
    base_url='https://cartoframes.carto.com/',
    api_key='default_public'
)

Map(Layer('spend_data'))
```

![Visualize the 'spend_data' dataset](../../img/guides/quickstart/quickstart-1.png)

### Change the viewport and basemap

By default, the map's center and zoom is set to encompass the entire dataset. For this map, let's modify these settings to better suite our area of interest:

```py
from cartoframes.viz import Map, Layer, basemaps

Map(
    Layer('spend_data'),
    viewport={'zoom': 2.51, 'lat': 42.99, 'lng': 24.73},
    basemap=basemaps.darkmatter,
    show_info=True
)
```

### Apply a SQL Query to your visualization

Next, let's filter the data by taking only the features where the purchase amount is between 150€ and 200€ using a simple SQL Query:

```py
from cartoframes.viz import Map, Layer, basemaps

Map(
    Layer('SELECT * FROM spend_data WHERE amount > 150 AND amount < 200')
)
```

![Apply a simple SQL Query](../../img/guides/quickstart/quickstart-2.png)

## Styles, Legends and Popups

To overwrite the default color and size of the points, we can modify the second parameter `Style` of the layer using the [CARTO VL String API](https://carto.com/developers/carto-vl/guides/style-with-expressions/). This API is very powerful because it allows you to style your visualizations with a few lines of code. 

But, as a data scientist, your primary focus is likely on the data vs. the visualization style, for this purpose,CARTOframes also provides you with a series of Helper Methods to create default visualization types.

First, let's take a look at how to change the default style and how to add legends and popups manually, which gives us more control, and then we'll use Helper Methods to get the final result.

### 1. Set the viewport

We're going to set the default viewport `zoom`, `lat` and `lng` for the visualization.

```py
from cartoframes.viz import Map, Layer

Map(
    Layer('spend_data'),
    viewport={'zoom': 12.03, 'lat': 41.4, 'lng': 2.19}
)
```

### 2. Change the Style

The style can be set directly as the **second** parameter of a Layer.

```py
from cartoframes.viz import Map, Layer

Map(
    Layer(
        'spend_data',
        'color: ramp($category, bold)'
    ),
    viewport={'zoom': 12.03, 'lat': 41.4, 'lng': 2.19}
)
```

![Style by $category](../../img/guides/quickstart/quickstart-3.png)

### 3. Add a basic Legend

In this case, the **third** parameter of a Layer is the Legend:

```py
from cartoframes.viz import Map, Layer

Map(
    Layer(
        'spend_data',
        'color: ramp($category, bold)',
        {'type': 'color-bins', 'title': 'Categories'}
    ),
    viewport={'zoom': 12.03, 'lat': 41.4, 'lng': 2.19}
)
```

![Add a legend for the styled category](../../img/guides/quickstart/quickstart-4.png)

### 4. Add a basic Popup

Now, let's add the Popup settings in the **fourth** parameter.

```py
from cartoframes.viz import Map, Layer

Map(
    Layer(
        'spend_data',
        'color: ramp($category, bold)',
        {'type': 'color-bins', 'title': 'Categories'}
        {
          'hover': [{
              'title': 'Category',
              'value': '$category'
          }, {
              'title': 'Hour',
              'value': '$hour'
          }]
        }
    ),
    viewport={'zoom': 12.03, 'lat': 41.4, 'lng': 2.19}
)
```

![Show popups when interacting with the features](../../img/guides/quickstart/quickstart-5.png)

## Use a built-in helper

CARTOframes has a set of built-in [Helper Methods]({{ site.url }}/developers/cartoframes/guides/helper-methods-part-1/) that can be used to create visualizations with default style, legends and popups, all together!.

```py
from cartoframes.viz import Map
from cartoframes.viz.helpers import color_bins_layer

Map(
    color_bins_layer('spend_data','amount', 'Spent Amount €'),
    viewport={'zoom': 12.03, 'lat': 41.4, 'lng': 2.19}
)
```

![Final visualization](../../img/guides/quickstart/quickstart-final.gif)