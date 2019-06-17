## Quickstart

### About this Guide

This guide is meant to guide you step by step from the installing and authentication process to generate a simple interactive visualization. The full notebook example can be found in the [01_basic_usage](https://github.com/CartoDB/cartoframes/blob/master/examples/01_quickstart/01_basic_usage.ipynb) notebook.

At the end, you'll be able to create a simple visualization like the one below and get a link to share it.

<img src="../../img/guides/quickstart/quickstart-final.gif" alt="Final visualization" />

### Installing CARTOframes

You can install CARTOframes with `pip`. Simply type the following in the command line to do a system install:

```bash
$ pip install cartoframes
```

To install through a Jupyter notebook, you can run

```bash
!pip install cartoframes
```

It is recommended to install cartoframes in a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/). For example, you can run the the following command line commands to create a virtual env, activate it, and install cartoframes:

```bash
$ virtualenv cfenv
$ source cfenv/bin/activate
(cfenv) $ pip install cartoframes
```

You'll notice the virtual environment name in your command line prompt, like above. Type `deactivate` to exit the virtualenv:

```bash
(cfenv) $ deactivate
```

### Installing Jupyter notebook

To install Jupyter, type:

```bash
$ pip install jupyter
```

If working in a virtual environment, make sure you have activated the environment first.

### Starting Jupyter notebook

Start up a Jupyter notebook with the following command:

```bash
$ jupyter notebook
```

After you type that command, you will see the notebook server starting up and a browser window with the directory contents open.

Next, create a new notebook. See Jupyter's [running a notebook](https://jupyter.readthedocs.io/en/latest/running.html#running) for more information.

### Authentication

Before we can do anything with CARTOframes, we need to authenticate against a CARTO account by passing in CARTO credentials. You will need your username (`base_url`) and an API key (`api_key`), which can be found at http://your_user_name.carto.com/your_apps.

If you don't have yet an account at CARTO, and you want to start learning how to use CARTOframes, you only need the cartoframes library. Take a look to the Sources examples to know how to visualize data from a Dataframe or a GeoJSON.

If you already have an account, you can start analyzing and visualizing your data! In this quickstart guide, we'll be using the [`spend_data`](https://cartoframes.carto.com/tables/spend_data/public/map) Dataset, which contains customer activity information in the city of Barcelona.

The elements we need to create contexts are under the `cartoframes.auth` namespace. For this Quickstart guide, let's use one the `cartoframes` account and a public dataset.

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer

set_default_context(
    base_url='https://cartoframes.carto.com/',
    api_key='default_public'
)

Map(Layer('spend_data'))
```

<img src="../../img/guides/quickstart/quickstart-1.png" alt="Visualize the 'spend_data' dataset" />

### Change the viewport and basemap

```py
from cartoframes.viz import Map, Layer, basemaps

Map(
    Layer('populated_places'),
    viewport={'zoom': 2.51, 'lat': 42.99, 'lng': 24.73},
    basemap=basemaps.darkmatter,
    show_info=True
)
```

### Apply an SQL Query to your visualization

In the next step we're filtering the data by taking only the features where the purchase amount is between 150€ and 200€. We're using a simple SQL Query:

```py
from cartoframes.viz import Map, Layer, basemaps

Map(
    Layer('SELECT * FROM spend_data WHERE amount > 150 AND amount < 200')
)
```

<img src="../../img/guides/quickstart/quickstart-2.png" alt="Apply a simple SQL Query" />

## Styles, Legends and Popups

In order to change the color and make them a bit bigger, we can change the style of the layer. The second parameter is the `Style` of the layer, and uses [CARTO VL String API](https://carto.com/developers/carto-vl/guides/style-with-expressions/). This API is very powerful because it allows you to style your visualizations with a few lines of code. However, from a data scientist perspective, sometimes we need to focus on the data and not in the visualization style itself. CARTOframes takes this responsibility by providing Helper Methods.

We'll se first how to change the default style and how to add legends and popups manually, which gives us more control, and then we'll use Helper Methods to get the final result.

### 1. Change the Style

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

<img src="../../img/guides/quickstart/quickstart-3.png" alt="Style by $category" />

### 2. Add a basic Legend

```py
from cartoframes.viz import Map, Layer, Legend

Map(
    Layer(
        'spend_data',
        'color: ramp($category, bold)',
        legend=Legend({
            'type': 'color-bins',
            'title': 'Categories'
        })
    ),
    viewport={'zoom': 12.03, 'lat': 41.4, 'lng': 2.19}
)
```

<img src="../../img/guides/quickstart/quickstart-4.png" alt="Add a legend for the styled category" />

### 3. Add a basic Popup

```py
from cartoframes.viz import Map, Layer, Legend, Popup

Map(
    Layer(
        'spend_data',
        'color: ramp($category, bold)',
        legend=Legend({
            'type': 'color-bins',
            'title': 'Categories'
        }),
        popup=Popup({
            'hover': [{
                'title': 'Category',
                'value': '$category'
            }, {
                'title': 'Hour',
                'value': '$hour'
            }]
        })
    ),
    viewport={'zoom': 12.03, 'lat': 41.4, 'lng': 2.19}
)
```

<img src="../../img/guides/quickstart/quickstart-5.png" alt="Show popups when interacting with the features" />

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

<img src="../../img/guides/quickstart/quickstart-final.gif" alt="Final visualization" />