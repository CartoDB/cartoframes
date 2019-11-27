## Explore and Visualize Data

### Introduction

### Data

This guide uses two datasets: a point dataset of simulated Starbucks locations in Brooklyn, New York and 15 minute walk time polygons around each store augmented with demographic variables from CARTO's [Data Observatory](). To follow along, you can get the [point dataset here](cartoframes/examples/files/starbucks_brooklyn_geocoded.csv) and the [polygon dataset here](cartoframes/examples/files/starbucks_brooklyn_iso_enriched.csv).

As a first step, load both datasets as [Pandas DataFrames](https://pandas.pydata.org/pandas-docs/stable/getting_started/dsintro.html#dataframe) into the notebook:

```python
import pandas

# store point locations
df_stores = pandas.read_csv('../files/starbucks_brooklyn_geocoded.csv')

# 15 minute walk time polygons
df_iso = pandas.read_csv('../files/starbucks_brooklyn_iso_enriched.csv')
```

### Add Layers to a Map

Next, import the Map and Layer classes from the [Viz namespace](/developers/cartoframes/reference/#heading-Viz)to visualize the datasets:

```python
from cartoframes.viz import Map, Layer

Map([
    Layer(df_iso),
    Layer(df_stores)
])
```
The resulting map draws the data with default symbology on top of CARTO's Positron basemap with the zoom and center set to the extent of the data:

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

### Explore Attributes

Before going further, let's take a look at the attributes in each dataset to get a sense of the information available to visualize and interact with.

First, let's explore the store location attributes. In this dataset we will use the fields `id_store` which is a unique identifier for each of the locations and `revenue` which provides the information about how much a particular store earned in the year 2018.

```python
df_stores
```

<div>
  <table>
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
<div>

In the isochrone layer, we will use the demographic attributes for population (`popcy`), median household income (`inccymedhh`), employed population (`lbfcyempl`), number of people with a bachelor's degree (`educybach`), and `id_store` which matches the unique id in the store points.

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

Now that we've taken a first look at the fields in the data and done a basic visualization, let's look at how we can use the map as a tool for visual and interactive exploration of the data to better understand the relationship between a store's annual revenue and the surrounding area's demographic characteristics.

#### Add Widgets

As we saw in the table summaries above, there are a variety of demographic attributes in the isochrone Layer that would be helpful to better understand the characteristics of each 15 minute walk area around each store. To make this information available while exploring each location on the map, we can add each attribute as a [Widget](developers/cartoframes/reference/#heading-Widgets). For this case specifically, we will use [Formula Widgets](/developers/cartoframes/examples/#example-formula-widget) to summarize the numeric demographic variables and a [Category Widget](/developers/cartoframes/examples/#example-category-widget) on the categorical attribute of `id_store`.

To add Widgets, we first need to import the types that we want to use and then inside of the `df_iso` Layer add one for each attribute of interest. The Formula Widget accepts different types of aggregations. For this map, we will aggregate each demographic variable using `sum` so the totals update as we zoom, pan and interact with the map. We will also label each Widget appropriately using the `title` parameter.

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

Pretty neat, right?!

#### Add Popups

In order to aid our map-based exploration, let's import the [Popup]() class and use the hover option on the `df_iso` Layer to be able to quickly identify a store by its ID:

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
Now, as you explore the map and summarize demographics, it is much easier to relate the summarized values to a unique store since you can hover over the area to see its ID.

#### Symbolize Store Points

Ok, so we have some really useful information available on the map but only coming from the isochrone Layer. In order to visually locate which stores are performing better than others, it would be extremely helpful to have the points sized by the attribute `revenue`.

A quick way to visualize numeric or categorical attributes is to use [Visualization Layers](). For this map, let's size the store points proportionate to their revenue using the `color_continuous_layer`

