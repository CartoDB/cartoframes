## Quickstart

### About this Guide

This guide is meant to guide you step by step from the installing and authentication process to generate a simple interactive visualization. The full notebook example can be found in the [01_basic_usage](https://github.com/CartoDB/cartoframes/blob/master/examples/01_quickstart/01_basic_usage.ipynb) notebook.

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

If you already have an account, you can start analyzing and visualizing your data!

The elements needed to create contexts are under the `cartoframes.auth` namespace. For this Quickstart guide, let's use one the `cartoframes` account and a public dataset:

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map, Layer

set_default_context(
    base_url='https://cartoframes.carto.com/',
    api_key='default_public'
)

Map(Layer('populated_places'))
```

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

We're filtering by Country using a SQL Query as the first parameter of the Layer we're creating. In this case, we're going to get only the features that belong to Spain.

```py
from cartoframes.viz import Map, Layer, basemaps

Map(
    Layer('SELECT * from populated_places WHERE adm0name = \'Spain\'')
)
```

## Styles, Legends and Popups

In order to change the color and make them a bit bigger, we can change the style of the layer. The second parameter is the `Style` of the layer, and uses [CARTO VL String API](https://carto.com/developers/carto-vl/guides/style-with-expressions/). This API is very powerful because it allows you to style your visualizations with a few lines of code. However, from a data scientist perspective, sometimes we need to focus on the data and not in the visualization style itself. CARTOframes takes this responsibility by providing Helper Methods.

We'll se first how to change the default style and how to add legends and popups manually, which gives us more control, and then we'll use Helper Methods to get the final result.

### 1. Change the Style

```py
from cartoframes.viz import Map, Layer, basemaps

Map(
    Layer(
      'SELECT * from populated_places WHERE adm0name = \'Spain\'',
      'color: purple width: 15'
    )
)
```

### 2. Add a basic Legend

```py
from cartoframes.viz import Legend

Map(
    Layer(
        'populated_places',
        'color: ramp($scalerank, purpor) width: 15',
        legend=Legend({
            'type': 'color-bins',
            'title': 'Scale Rank'
        })
    )
)
```

### 3. Add a basic Popup

```py
from cartoframes.viz import Popup

Map(
    Layer(
        'populated_places',
        'color: ramp($scalerank, purpor) width: 15',
        legend=Legend({
            'type': 'color-bins',
            'title': 'Scale Rank'
        }),
        popup=Popup({
            'hover': [{
                'title': 'Name',
                'value': '$name'
            }, {
                'title': 'Province',
                'value': '$adm1name'
            }]
        })
    )
)
```

## Use a built-in helper

CARTOframes has a set of built-in [Helper Methods]({{ site.url }}/documentation/cartoframes/guides/helper-methods-part-1/) that can be used to create visualizations with default style, legends and popups, all together!.

```py
from cartoframes.viz.helpers import color_bins_layer

Map(
    color_bins_layer('populated_places','scalerank', 'Scale Rank')
)
```