## Visualization

### Introduction

As a data scientist, you likely work through a data exploration processes on nearly every project. Exploratory data analysis can entail many things from finding relevant data and cleaning it to running analysis and building models. The ability to visually analyze and interact with data is key during the exploratory process and the final presentation of insights.

With that in mind, this guide introduces the basic building blocks for creating web-based, dynamic, and interactive map visualizations inside of a Jupyter Notebook with CARTOframes.

In this guide you are introduced to the Map and Layer classes, how to explore data with Widgets and Popups, how to use Visualization Layers to quickly symbolize thematic attributes, and options for creating maps to share your findings.

### Data

This guide uses two datasets: a point dataset of simulated Starbucks locations in Brooklyn, New York and 15 minute walk time polygons (isochrones) around each store augmented with demographic variables from CARTO's [Data Observatory](). To follow along, you can get the [point dataset here](https://github.com/CartoDB/cartoframes/blob/develop/examples/files/starbucks_brooklyn_geocoded.csv) and the [polygon dataset here](https://github.com/CartoDB/cartoframes/blob/develop/examples/files/starbucks_brooklyn_iso_enriched.csv).

As a first step, load both datasets as [Pandas DataFrames](https://pandas.pydata.org/pandas-docs/stable/getting_started/dsintro.html#dataframe) into the notebook:

```python
import pandas

# store point locations
df_stores = pandas.read_csv('../files/starbucks_brooklyn_geocoded.csv')

# 15 minute walk time polygons
df_iso = pandas.read_csv('../files/starbucks_brooklyn_iso_enriched.csv')
```

### Add Layers to a Map

Next, import the Map and Layer classes from the [Viz namespace](/developers/cartoframes/reference/#heading-Viz)to visualize the two datasets:

```python
from cartoframes.viz import Map, Layer

Map([
    Layer(df_iso),
    Layer(df_stores)
])
```

The resulting map draws each dataset with default symbology on top of CARTO's Positron basemap with the zoom and center set to the extent of both datasets:

<div class="example-map">
    <iframe
        id="viz_guide_add_layers_to_map"
        src="https://cartoframes.carto.com/kuviz/933d429c-a844-4c6b-8bc3-0d02e1737dbc"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

> To learn more about basemap options, visit the Map Configuration [Examples](/developers/cartoframes/examples/) section of the CARTOframes Developer Center

### Explore Attributes

Before going further, take a look at the attributes in each dataset to get a sense of the information available to visualize and interact with.

First, explore the store location attributes. In this dataset you will use the fields:
* `id_store` that is a unique identifier for each of the locations
* `revenue` which provides the information about how much a particular store earned in the year 2018

```python
df_stores
```

<div>
  <table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>the_geom</th>
      <th>cartodb_id</th>
      <th>field_1</th>
      <th>name</th>
      <th>address</th>
      <th>revenue</th>
      <th>id_store</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0101000020E61000005EA27A6B607D52C01956F146E655...</td>
      <td>1</td>
      <td>0</td>
      <td>Franklin Ave &amp; Eastern Pkwy</td>
      <td>341 Eastern Pkwy,Brooklyn, NY 11238</td>
      <td>1321040.772</td>
      <td>A</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0101000020E6100000B610E4A0847D52C0B532E197FA49...</td>
      <td>2</td>
      <td>1</td>
      <td>607 Brighton Beach Ave</td>
      <td>607 Brighton Beach Avenue,Brooklyn, NY 11235</td>
      <td>1268080.418</td>
      <td>B</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0101000020E6100000E5B8533A587F52C05726FC523F4F...</td>
      <td>3</td>
      <td>2</td>
      <td>65th St &amp; 18th Ave</td>
      <td>6423 18th Avenue,Brooklyn, NY 11204</td>
      <td>1248133.699</td>
      <td>C</td>
    </tr>
  </tbody>
</table>
</div>

From the isochrone Layer, you will use the demographic attributes:

* `popcy` which counts the total population in each area
* `inccymedhh` that is the median household income in each area
* `lbfcyempl` counts the employed population
* `educybach` counts the number of people with a bachelor's degree
* `id_store` which matches the unique id in the store points

```python
df_iso
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>the_geom</th>
      <th>cartodb_id</th>
      <th>popcy</th>
      <th>data_range</th>
      <th>range_label</th>
      <th>lbfcyempl</th>
      <th>educybach</th>
      <th>inccymedhh</th>
      <th>id_store</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0106000020E61000000100000001030000000100000033...</td>
      <td>3</td>
      <td>1311.667005</td>
      <td>900</td>
      <td>15 min.</td>
      <td>568.006658</td>
      <td>151.682217</td>
      <td>48475.834346</td>
      <td>C</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0106000020E61000000100000001030000000100000033...</td>
      <td>7</td>
      <td>2215.539290</td>
      <td>900</td>
      <td>15 min.</td>
      <td>1181.265882</td>
      <td>313.739810</td>
      <td>35125.870621</td>
      <td>G</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0106000020E61000000100000001030000000100000033...</td>
      <td>9</td>
      <td>1683.229186</td>
      <td>900</td>
      <td>15 min.</td>
      <td>1012.737753</td>
      <td>449.871005</td>
      <td>87079.135091</td>
      <td>I</td>
    </tr>
  </tbody>
</table>
</div>

### Visual and Interactive Data Exploration

Now that you've taken a first look at the fields in the data and done a basic visualization, let's look at how you can use the map as a tool for visual and interactive exploration to better understand the relationship between a store's annual revenue and the surrounding area's demographic characteristics.

#### Add Widgets

As seen in the table summaries above, there are a variety of demographic attributes in the isochrone Layer that would be helpful to better understand the characteristics around each store.

To make this information available while exploring each location on the map, you can add each attribute as a [Widget](developers/cartoframes/reference/#heading-Widgets). For this case specifically, you will use [Formula Widgets](/developers/cartoframes/examples/#example-formula-widget) to summarize the demographic variables and a [Category Widget](/developers/cartoframes/examples/#example-category-widget) on the categorical attribute of `id_store`.

To add Widgets, you first need to import the types that you want to use and then, inside of the `df_iso` Layer add one widget for each attribute of interest. The Formula Widget accepts different types of aggregations. For this map, we will aggregate each demographic variable using `sum` so the totals update as we zoom, pan and interact with the map. We will also label each Widget appropriately using the `title` parameter.

```python
from cartoframes.viz.widgets import formula_widget, category_widget

Map([
    Layer(
        df_iso,
        widgets=[
            formula_widget(
                'popcy',
                'sum',
                title='Total Population Served'
            ),
            formula_widget(
                'inccymedhh',
                'sum',
                title='Median Income ($)'
            ),
            formula_widget(
                'lbfcyempl',
                'sum',
                title='Employed Population',
            ),
            formula_widget(
                'educybach',
                'sum',
                title='Number of People with Bachelor Degree',
            ),
            category_widget(
                'id_store',
                title='Store ID'
            )
        ]
    ),
    Layer(
        df_stores
    )
])
```
At this point, take a few minutes to explore the map to see how the Widget values update. For example, select a Store ID from the Category Widget to summarize the demographics for a particular store. Alternatively, zoom and pan the map to get summary statistics for the features in the current map view.

#### Add Popups

In order to aid this map-based exploration, import the [Popup](developers/cartoframes/examples/#example-popup-on-hover) class and use the hover option on the `df_iso` Layer to be able to quickly hover over stores and get their ID:

```python
from cartoframes.viz import Popup

Map([
    Layer(
        df_iso,
        widgets=[
            formula_widget(
                'popcy',
                'sum',
                title='Total Population Served'
            ),
            formula_widget(
                'inccymedhh',
                'sum',
                title='Median Income ($)'
            ),
            formula_widget(
                'lbfcyempl',
                'sum',
                title='Employed Population',
            ),
            formula_widget(
                'educybach',
                'sum',
                title='Number of People with Bachelor Degree',
            ),
            category_widget(
                'id_store',
                title='Store ID'
            )
        ],
        popup=Popup({
            'hover': {
                'title': 'Store ID',
                'value': '$id_store'
            }
        })
    ),
    Layer(
        df_stores
    )
])
```
Now, as you explore the map and summarize demographics, it is much easier to relate the summarized values to a unique store ID.

#### Symbolize Store Points

At this point, you have some really useful information available on the map but only coming from the isochrone Layer. Sizing the store points by the attribute `revenue` will provide a way to visually locate which stores are performing better than others. A quick way to visualize numeric or categorical attributes during the data exploration process is to take advantage of [Visualization Layers](/developers/cartoframes/reference/#heading-Helpers).

To size the store points proportionate to their revenue, we'll use the [`size_continuous_layer`](/developers/cartoframes/examples/#example-size-continuous-layer):

```python
from cartoframes.viz.helpers import size_continuous_layer

Map([
    Layer(
        df_iso,
        widgets=[
            formula_widget(
                'popcy',
                'sum',
                title='Total Population Served'
            ),
            formula_widget(
                'inccymedhh',
                'sum',
                title='Median Income ($)'
            ),
            formula_widget(
                'lbfcyempl',
                'sum',
                title='Employed Population',
            ),
            formula_widget(
                'educybach',
                'sum',
                title='Number of People with Bachelor Degree',
            ),
            category_widget(
                'id_store',
                title='Store ID'
            )
        ],
        popup=Popup({
            'hover': {
                'title': 'Store ID',
                'value': '$id_store'
            }
        })
    ),
    size_continuous_layer(
        df_stores,
        'revenue'
    )
])
```

Now you have a proportional symbol map where points are sized by revenue. You will also notice that an appropriate legend has been added to the map and when you hover over the points, you will see each store's revenue value.

Next, let's take a look at how to modify some of the defaults.

Every Visualization Layer has a set of paramaters available to customize the defaults to better suit a given map. A quick way to see which parameters are available for customization in the `size_continuous_layer`, is to run `help(size_continuous_layer)` in a notebook cell.

Let's make a few adjustments to make it easier to distinguish and locate the highest and lowest performing stores:

* The continuous point size reads between a minimum and maximum range of symbol sizes. Since the smallest revenue value on this map is hard to see, set `size=[10,50]`
* By default both the Legend and Popup titles are set to the attribute being visualized. To give them more descriptive titles, set `title=Annual Revenue ($)`
* In order to see and interact with the distribution of revenue values, we can also add a Histogram Widget (turned off by default) by setting `widget=True`

```python
size_continuous_layer(
    df_stores,
    'revenue',
    size=[10,50],
    title='Annual Revenue ($)',
    widget=True
)
```

And now you have a map to visually and interactively explore the relationship between revenue and demographic variables for each store:

<div class="example-map">
    <iframe
        id="viz_guide_add_layers_to_map"
        src="https://cartoframes.carto.com/kuviz/ef09536b-3534-4bb1-8380-5e48eeaf6821"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

## Insights

The map above provides a way to explore the data both visually and interactively in different ways:

* you can almost instantaneously locate higher and lower performing stores based on the symbol sizes
* you can zoom in on any store to summarize demographic characteristics
* you can quickly find out the store ID by hovering on it
* you can select a range of revenues from the Histogram Widget and have the map update to only display those stores
* you can use the Store ID Category Widget to isolate a particular store and summarize values

Use the map to see if you can find the highest and lowest performing stores and summarize the demographic characteristics of each one!

## Present Insights

Now that you have gained insight into the relationship between revenue and demographics, let's say that the most influential factor of how well a store performed was median income and you want to create a map to show that particular relationship.

To show this, the map below uses another Visualization Layer, this time the [`color_bins_layer`](/developers/cartoframes/examples/#example-color-bins-layer) to color each isochrone according to the range of median household income it falls within. Additionally, the `size_continuous_layer` used in the previous map has been further customized to account for the new thematic median income style, and the store points have been added again as a third Layer to show their location and ID on hover. The map also has a custom [viewport](https://carto.com/developers/cartoframes/examples/#example-set-custom-viewport) set to center it on the highest performing (A) and lowest performing (J) stores that have similar median income values.

```python
from cartoframes.viz.helpers import color_bins_layer

Map([
    color_bins_layer(
        df_iso,
        'inccymedhh',
        bins=7,
        palette='pinkyl',
        opacity=0.8,
        stroke_width=0,
        title='Median Household Income ($)',
        footer='Source: US Census Bureau'
    ),
    size_continuous_layer(
        df_stores,
        'revenue',
        size=[10,50],
        range_max=1000000,
        opacity=0,
        stroke_color='turquoise',
        stroke_width=2,
        title='Annual Revenue ($)',
        description='Reported in 2018'
    ),
    Layer(
        df_stores,
        popup=Popup({
            'hover': {
                'title': 'Store ID',
                'value': '$id_store'
            }
        })
    )
], viewport={'zoom': 12, 'lat': 40.644417, 'lng': -73.934710})
```

<div class="example-map">
    <iframe
        id="viz_guide_present_insights"
        src="https://cartoframes.carto.com/kuviz/3db3ffd9-8aa8-4b6d-8429-ace219c68134"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

### Compare Variables with a Layout

If you want to compare store revenue with multiple demographic variables, you can create a [Layout](https://carto.com/developers/cartoframes/examples/#example-custom-layout) with multiple maps.

In the example below, one map symbolizes annual revenue and the other three maps symbolize three demographic variables that use the same color palette where yellow is low and red is high. Each map has a title to label which attribute is being mapped.

```python
from cartoframes.viz import Layout

Layout([
    Map([
        size_continuous_layer(
            df_stores,
            'revenue',
            size=[10,50],
            range_max=1000000,
            opacity=0,
            stroke_color='turquoise',
            stroke_width=2,
            title='Annual Revenue',
            popup=False
        ),
        Layer(df_stores)
    ]),
    Map([
        color_bins_layer(
            df_iso,
            'inccymedhh',
            bins=7,
            palette='pinkyl',
            stroke_width=0,
            title='Median Income',
            popup=False
        ),
        Layer(df_stores)
    ]),
    Map([
        color_bins_layer(
            df_iso,
            'popcy',
            bins=7,
            palette='pinkyl',
            stroke_width=0,
            title='Total Pop',
            popup=False
        ),
        Layer(df_stores)
    ]),
    Map([
        color_bins_layer(
            df_iso,
            'lbfcyempl',
            bins=7,
            palette='pinkyl',
            stroke_width=0,
            title='Employed Pop',
            popup=False
        ),
        Layer(df_stores)
    ]),
],2,2,viewport={'zoom': 10, 'lat': 40.64, 'lng': -73.92}, map_height=400)
```

<div class="example-map">
    <iframe
        id="viz_guide_layout"
        src="https://cartoframes.carto.com/kuviz/312ce7b0-d5c1-4cc7-9a79-584cfea598a2"
        width="100%"
        height="800"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>
