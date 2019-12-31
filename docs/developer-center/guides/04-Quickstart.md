## Quickstart

### Introduction

Hi! Glad to see you made it to the Quickstart guide! In this guide you are introduced to how CARTOframes can be used by data scientists in spatial analysis workflows. Using simulated Starbucks revenue data, this guide walks through some common steps a data scientist takes to answer the following question: which stores are performing better than others?

Before you get started, we encourage you to have CARTOframes installed so you can get a feel for the library by using it:

```
pip install --pre cartoframes
```

For additional ways to install CARTOframes, check out the [Installation Guide](/developers/cartoframes/guides/Installation).

#### Spatial analysis scenario

Let's say you are a data scientist working for Starbucks and you want to better understand why some stores in Brooklyn, New York, perform better than others.

To begin, let's outline a workflow:

- Get and explore your company's data
- Create areas of influence for your stores
- Enrich your data with demographic data
- And finally, share the results of your analysis with your team

Let's get started!

### Get and explore your company's data

[Use this dataset](https://libs.cartocdn.com/cartoframes/files/starbucks_brooklyn.csv) to start your exploration. It contains information about the location of Starbucks and each store's annual revenue.

As a first exploratory step, read it into a Jupyter Notebook using [pandas](https://pandas.pydata.org/).

```python
import pandas as pd

stores_df = pd.read_csv('https://libs.cartocdn.com/cartoframes/files/starbucks_brooklyn.csv')
stores_df.head()
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>address</th>
      <th>revenue</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Franklin Ave &amp; Eastern Pkwy</td>
      <td>341 Eastern Pkwy,Brooklyn, NY 11238</td>
      <td>1321040.772</td>
    </tr>
    <tr>
      <th>1</th>
      <td>607 Brighton Beach Ave</td>
      <td>607 Brighton Beach Avenue,Brooklyn, NY 11235</td>
      <td>1268080.418</td>
    </tr>
    <tr>
      <th>2</th>
      <td>65th St &amp; 18th Ave</td>
      <td>6423 18th Avenue,Brooklyn, NY 11204</td>
      <td>1248133.699</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Bay Ridge Pkwy &amp; 3rd Ave</td>
      <td>7419 3rd Avenue,Brooklyn, NY 11209</td>
      <td>1185702.676</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Caesar's Bay Shopping Center</td>
      <td>8973 Bay Parkway,Brooklyn, NY 11214</td>
      <td>1148427.411</td>
    </tr>
  </tbody>
</table>
</div>

To display your stores as points on a map, you first have to convert the `address` column into geometries. This process is called [geocoding](https://carto.com/help/working-with-data/geocoding-types/) and CARTO provides a straightforward way to do it (you can learn more about it in the [Location Data Services guide](/developers/cartoframes/guides/Location-Data-Services)).

In order to geocode, you have to set your CARTO credentials. If you aren't sure about your API key, check the [Authentication guide](/developers/cartoframes/guides/Authentication/) to learn how to get it. In case you want to see the geocoded result, without being logged in, [you can get it here](https://libs.cartocdn.com/cartoframes/files/starbucks_brooklyn_geocoded.csv).

> Note: If you don't have an account yet, you can get a trial, or a free account if you are a student, by [signing up here](https://carto.com/signup/).

```python
from cartoframes.auth import set_default_credentials

set_default_credentials('creds.json')
```

Now that your credentials are set, we are ready to geocode the dataframe. The resulting data will be a [CartoDataFrame](/developers/cartoframes/reference#heading-CartoDataFrame), a dataframe that integrates with CARTO services that extends on the functionality of [GeoDataFrames](http://geopandas.org/data_structures.html#geodataframe). CARTOframes is built on top of [GeoPandas](http://geopandas.org/) to guarantee compatibility between both libraries, and all [GeoDataFrame](http://geopandas.org/data_structures.html#geodataframe) operations are available.


```python
from cartoframes.data.services import Geocoding

stores_cdf, _ = Geocoding().geocode(stores_df, street='address')
stores_cdf.head()
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>the_geom</th>
      <th>name</th>
      <th>address</th>
      <th>revenue</th>
      <th>gc_status_rel</th>
      <th>carto_geocode_hash</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>POINT (-73.95901 40.67109)</td>
      <td>Franklin Ave &amp; Eastern Pkwy</td>
      <td>341 Eastern Pkwy,Brooklyn, NY 11238</td>
      <td>1321040.772</td>
      <td>0.91</td>
      <td>9212e0e908d8c64d07c6a94827322397</td>
    </tr>
    <tr>
      <th>1</th>
      <td>POINT (-73.96122 40.57796)</td>
      <td>607 Brighton Beach Ave</td>
      <td>607 Brighton Beach Avenue,Brooklyn, NY 11235</td>
      <td>1268080.418</td>
      <td>0.97</td>
      <td>b1bbfe2893914a350193969a682dc1f5</td>
    </tr>
    <tr>
      <th>2</th>
      <td>POINT (-73.98976 40.61912)</td>
      <td>65th St &amp; 18th Ave</td>
      <td>6423 18th Avenue,Brooklyn, NY 11204</td>
      <td>1248133.699</td>
      <td>0.95</td>
      <td>e47cf7b16d6c9b53c63e86a0418add1d</td>
    </tr>
    <tr>
      <th>3</th>
      <td>POINT (-74.02744 40.63152)</td>
      <td>Bay Ridge Pkwy &amp; 3rd Ave</td>
      <td>7419 3rd Avenue,Brooklyn, NY 11209</td>
      <td>1185702.676</td>
      <td>0.95</td>
      <td>2f21749c02f73116892eb3b6fd5d5738</td>
    </tr>
    <tr>
      <th>4</th>
      <td>POINT (-74.00098 40.59321)</td>
      <td>Caesar's Bay Shopping Center</td>
      <td>8973 Bay Parkway,Brooklyn, NY 11214</td>
      <td>1148427.411</td>
      <td>0.95</td>
      <td>134c23973313802448365db6235783f9</td>
    </tr>
  </tbody>
</table>
</div>

Done! Now that the stores are geocoded, you will notice a new column named `geometry` has been added. This column stores the geographic location of each store and it's used to plot each location on the map.

You can quickly visualize your geocoded dataframe using the Map and Layer classes. Check out the [Visualization guide](/developers/cartoframes/guides/Visualization) to learn more about the visualization capabilities inside of CARTOframes.

```python
from cartoframes.viz import Map, Layer

Map(Layer(stores_cdf))
```

<div class="example-map">
    <iframe
        id="quickstart_guide_starbucks_brooklyn"
        src="https://cartoframes.carto.com/kuviz/7ac17374-7667-44bf-8252-5f8e7370e3e8"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

Great! You have a map!

With the stores plotted on the map, you now have a better sense about where each one is. To continue your exploration, you want to know which stores earn the most yearly revenue. To do this, you can use the [`size_continuous_layer`](/developers/cartoframes/examples/#example-size-continuous-layer) visualization layer:

```python
from cartoframes.viz.helpers import size_continuous_layer

Map(size_continuous_layer(stores_cdf, 'revenue', 'Annual Revenue ($)'))
```

<div class="example-map">
    <iframe
        id="quickstart_guide_starbucks_brooklyn_by_revenue"
        src="https://cartoframes.carto.com/kuviz/7611a80b-0796-4eef-b3f0-a84135dacfd8"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

Good job! By using the [`size continuous visualization layer`](/developers/cartoframes/examples/#example-size-continuous-layer) you can see right away where the stores with higher revenue are. By default, visualization layers also provide a popup with the mapped value and an appropriate legend.

### Create your areas of influence

Similar to geocoding, there is a straightforward method for creating isochrones to define areas of influence around each store. Isochrones are concentric polygons that display equally calculated levels over a given surface area measured by time.

For this analysis, let's create isochrones for each store that cover the area within a 15 minute walk.

To do this you will use the Isolines data service:


```python
from cartoframes.data.services import Isolines

isochrones_cdf, _ = Isolines().isochrones(stores_cdf, [15*60], mode='walk')
isochrones_cdf.head()
```
<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>source_id</th>
      <th>data_range</th>
      <th>lower_data_range</th>
      <th>the_geom</th>
      <th>range_label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-73.95933 40.68012, -73.96074 ...</td>
      <td>15 min.</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-73.96187 40.58632, -73.96288 ...</td>
      <td>15 min.</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-73.99081 40.62694, -73.99169 ...</td>
      <td>15 min.</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-74.02850 40.64063, -74.02881 ...</td>
      <td>15 min.</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-74.00110 40.60186, -74.00249 ...</td>
      <td>15 min.</td>
    </tr>
  </tbody>
</table>
</div>


```python
map = Map([
    Layer(isochrones_cdf),
    Layer(stores_cdf)]
)
map
```

<div class="example-map">
    <iframe
        id="quickstart_guide_starbucks_brooklyn_iso"
        src="https://cartoframes.carto.com/kuviz/17291073-7c93-431e-9dad-07e5da307a6f"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

There they are! To learn more about creating isochrones and isodistances check out the [Location Data Services guide](/developers/cartoframes/guides/Location-Data-Services).

> Note: You will see how to publish a map in the last section. If you already want to publish this map, you can do it by calling `map.publish('starbucks_isochrones', password=None)`.


### Enrich your data with demographic data

Now that you have the area of influence calculated for each store, let's take a look at how to augment the result with population information to help better understand a store's average revenue per person.

> Note: To be able to use the Enrichment functions you need an enterprise CARTO account with Data Observatory 2.0 enabled. Contact your CSM or contact us at [sales@carto.com](mailto:sales@carto.com) for more information.


First, let's find the demographic variable we need. We will use the `Catalog` class that can be filter by country and category. In our case, we have to look for USA demographics datasets. Let's see which public ones are available.

```python
from cartoframes.data.observatory import Catalog

datasets_df = Catalog().country('usa').category('demographics').datasets.to_dataframe()
datasets_df[datasets_df['is_public_data'] == True]
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>available_in</th>
      <th>category_id</th>
      <th>category_name</th>
      <th>country_id</th>
      <th>data_source_id</th>
      <th>description</th>
      <th>geography_description</th>
      <th>geography_id</th>
      <th>geography_name</th>
      <th>id</th>
      <th>...</th>
      <th>lang</th>
      <th>name</th>
      <th>provider_id</th>
      <th>provider_name</th>
      <th>slug</th>
      <th>summary_json</th>
      <th>temporal_aggregation</th>
      <th>time_coverage</th>
      <th>update_frequency</th>
      <th>version</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_b758e778</td>
      <td>{'counts': {'rows': 220333, 'cells': 36354945,...</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>8</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2009)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_97b40c3b</td>
      <td>{'counts': {'rows': 51, 'cells': 12852, 'null_...</td>
      <td>yearly</td>
      <td>[2009-01-01,2010-01-01)</td>
      <td>None</td>
      <td>2009</td>
    </tr>
    <tr>
      <th>9</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2011)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_8074b548</td>
      <td>{'counts': {'rows': 52, 'cells': 13104, 'null_...</td>
      <td>yearly</td>
      <td>[2011-01-01,2012-01-01)</td>
      <td>None</td>
      <td>2011</td>
    </tr>
    <tr>
      <th>10</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2014)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_f01e41c7</td>
      <td>{'counts': {'rows': 52, 'cells': 13208, 'null_...</td>
      <td>yearly</td>
      <td>[2014-01-01,2015-01-01)</td>
      <td>None</td>
      <td>2014</td>
    </tr>
    <tr>
      <th>11</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2012)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_197de4f2</td>
      <td>{'counts': {'rows': 52, 'cells': 13104, 'null_...</td>
      <td>yearly</td>
      <td>[2012-01-01,2013-01-01)</td>
      <td>None</td>
      <td>2012</td>
    </tr>
    <tr>
      <th>12</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2017)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_6917107d</td>
      <td>{'counts': {'rows': 52, 'cells': 13104, 'null_...</td>
      <td>yearly</td>
      <td>[2017-01-01,2018-01-01)</td>
      <td>None</td>
      <td>2017</td>
    </tr>
    <tr>
      <th>13</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2013)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_6e7ad464</td>
      <td>{'counts': {'rows': 52, 'cells': 13104, 'null_...</td>
      <td>yearly</td>
      <td>[2013-01-01,2014-01-01)</td>
      <td>None</td>
      <td>2013</td>
    </tr>
    <tr>
      <th>14</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_31d9e865</td>
      <td>{'counts': {'rows': 220333, 'cells': 36354945,...</td>
      <td>5yrs</td>
      <td>[2009-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20092013</td>
    </tr>
    <tr>
      <th>15</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_69f1cc12</td>
      <td>{'counts': {'rows': 220333, 'cells': 36795611,...</td>
      <td>5yrs</td>
      <td>[2010-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>16</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Census Tracts (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Tracts level (2006 - 2...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_d4b2cf03</td>
      <td>{'counts': {'rows': 74002, 'cells': 17464472, ...</td>
      <td>5yrs</td>
      <td>[2006-01-01,2011-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
    <tr>
      <th>18</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2013)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_beb27e5f</td>
      <td>{'counts': {'rows': 828, 'cells': 208656, 'nul...</td>
      <td>yearly</td>
      <td>[2013-01-01,2014-01-01)</td>
      <td>None</td>
      <td>2013</td>
    </tr>
    <tr>
      <th>19</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2014)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_20d6ebfc</td>
      <td>{'counts': {'rows': 828, 'cells': 210312, 'nul...</td>
      <td>yearly</td>
      <td>[2014-01-01,2015-01-01)</td>
      <td>None</td>
      <td>2014</td>
    </tr>
    <tr>
      <th>20</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2015)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_57d1db6a</td>
      <td>{'counts': {'rows': 830, 'cells': 205840, 'nul...</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>21</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2016)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_ced88ad0</td>
      <td>{'counts': {'rows': 831, 'cells': 204426, 'nul...</td>
      <td>yearly</td>
      <td>[2016-01-01,2017-01-01)</td>
      <td>None</td>
      <td>2016</td>
    </tr>
    <tr>
      <th>22</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2017)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_b9dfba46</td>
      <td>{'counts': {'rows': 837, 'cells': 210924, 'nul...</td>
      <td>yearly</td>
      <td>[2017-01-01,2018-01-01)</td>
      <td>None</td>
      <td>2017</td>
    </tr>
    <tr>
      <th>23</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2018)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_2960a7d7</td>
      <td>{'counts': {'rows': 838, 'cells': 211176, 'nul...</td>
      <td>yearly</td>
      <td>[2018-01-01,2019-01-01)</td>
      <td>None</td>
      <td>2018</td>
    </tr>
    <tr>
      <th>26</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at States level (2006 - 2010)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_1b4fe990</td>
      <td>{'counts': {'rows': 52, 'cells': 12272, 'null_...</td>
      <td>5yrs</td>
      <td>[2006-01-01,2011-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
    <tr>
      <th>27</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at States level (2007 - 2011)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_5128f0b6</td>
      <td>{'counts': {'rows': 52, 'cells': 13104, 'null_...</td>
      <td>5yrs</td>
      <td>[2007-01-01,2012-01-01)</td>
      <td>None</td>
      <td>20072011</td>
    </tr>
    <tr>
      <th>28</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at States level (2008 - 2012)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_4a7136dd</td>
      <td>{'counts': {'rows': 52, 'cells': 13104, 'null_...</td>
      <td>5yrs</td>
      <td>[2008-01-01,2013-01-01)</td>
      <td>None</td>
      <td>20082012</td>
    </tr>
    <tr>
      <th>29</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at States level (2009 - 2013)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_162ffb</td>
      <td>{'counts': {'rows': 52, 'cells': 13104, 'null_...</td>
      <td>5yrs</td>
      <td>[2009-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20092013</td>
    </tr>
    <tr>
      <th>30</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at States level (2010 - 2014)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_583e0b8c</td>
      <td>{'counts': {'rows': 52, 'cells': 13208, 'null_...</td>
      <td>5yrs</td>
      <td>[2010-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>31</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at States level (2011 - 2015)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_125912aa</td>
      <td>{'counts': {'rows': 52, 'cells': 12896, 'null_...</td>
      <td>5yrs</td>
      <td>[2011-01-01,2016-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>32</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at States level (2012 - 2016)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_ccf039c0</td>
      <td>{'counts': {'rows': 52, 'cells': 12792, 'null_...</td>
      <td>5yrs</td>
      <td>[2012-01-01,2017-01-01)</td>
      <td>None</td>
      <td>20122016</td>
    </tr>
    <tr>
      <th>33</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at States level (2013 - 2017)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_869720e6</td>
      <td>{'counts': {'rows': 52, 'cells': 13104, 'null_...</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>34</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2007)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_700c213c</td>
      <td>{'counts': {'rows': 51, 'cells': 12852, 'null_...</td>
      <td>yearly</td>
      <td>[2007-01-01,2008-01-01)</td>
      <td>None</td>
      <td>2007</td>
    </tr>
    <tr>
      <th>35</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2008)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_e0b33cad</td>
      <td>{'counts': {'rows': 51, 'cells': 12852, 'null_...</td>
      <td>yearly</td>
      <td>[2008-01-01,2009-01-01)</td>
      <td>None</td>
      <td>2008</td>
    </tr>
    <tr>
      <th>36</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2010)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_f77385de</td>
      <td>{'counts': {'rows': 52, 'cells': 12844, 'null_...</td>
      <td>yearly</td>
      <td>[2010-01-01,2011-01-01)</td>
      <td>None</td>
      <td>2010</td>
    </tr>
    <tr>
      <th>37</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2018)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_f9a80dec</td>
      <td>{'counts': {'rows': 52, 'cells': 13104, 'null_...</td>
      <td>yearly</td>
      <td>[2018-01-01,2019-01-01)</td>
      <td>None</td>
      <td>2018</td>
    </tr>
    <tr>
      <th>38</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_z...</td>
      <td>5-digit Zip Code Tabluation Areas (2015) - sho...</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at 5-digit Zip Code Tabluation A...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_844c94b6</td>
      <td>{'counts': {'rows': 33120, 'cells': 8346240, '...</td>
      <td>5yrs</td>
      <td>[2007-01-01,2012-01-01)</td>
      <td>None</td>
      <td>20072011</td>
    </tr>
    <tr>
      <th>39</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_60e73728</td>
      <td>{'counts': {'rows': 220333, 'cells': 36354945,...</td>
      <td>5yrs</td>
      <td>[2007-01-01,2012-01-01)</td>
      <td>None</td>
      <td>20072011</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>43</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Census Tracts (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Tracts level (2007 - 2...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_9ed5d625</td>
      <td>{'counts': {'rows': 74001, 'cells': 18648252, ...</td>
      <td>5yrs</td>
      <td>[2007-01-01,2012-01-01)</td>
      <td>None</td>
      <td>20072011</td>
    </tr>
    <tr>
      <th>44</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Census Tracts (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Tracts level (2008 - 2...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_858c104e</td>
      <td>{'counts': {'rows': 74001, 'cells': 18648252, ...</td>
      <td>5yrs</td>
      <td>[2008-01-01,2013-01-01)</td>
      <td>None</td>
      <td>20082012</td>
    </tr>
    <tr>
      <th>45</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Census Tracts (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Tracts level (2009 - 2...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_cfeb0968</td>
      <td>{'counts': {'rows': 74001, 'cells': 18648252, ...</td>
      <td>5yrs</td>
      <td>[2009-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20092013</td>
    </tr>
    <tr>
      <th>46</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Census Tracts (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Tracts level (2010 - 2...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_97c32d1f</td>
      <td>{'counts': {'rows': 74001, 'cells': 18796254, ...</td>
      <td>5yrs</td>
      <td>[2010-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>47</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Census Tracts (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Tracts level (2011 - 2...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_dda43439</td>
      <td>{'counts': {'rows': 74001, 'cells': 18352248, ...</td>
      <td>5yrs</td>
      <td>[2011-01-01,2016-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>48</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Census Tracts (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Tracts level (2012 - 2...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_30d1f53</td>
      <td>{'counts': {'rows': 74001, 'cells': 17908242, ...</td>
      <td>5yrs</td>
      <td>[2012-01-01,2017-01-01)</td>
      <td>None</td>
      <td>20122016</td>
    </tr>
    <tr>
      <th>49</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Census Tracts (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Tracts level (2013 - 2...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_496a0675</td>
      <td>{'counts': {'rows': 74001, 'cells': 18648252, ...</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>50</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Counties level (2006 - 2010)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_11fe9c96</td>
      <td>{'counts': {'rows': 3221, 'cells': 760156, 'nu...</td>
      <td>5yrs</td>
      <td>[2006-01-01,2011-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
    <tr>
      <th>51</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Counties level (2007 - 2011)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_5b9985b0</td>
      <td>{'counts': {'rows': 3221, 'cells': 811692, 'nu...</td>
      <td>5yrs</td>
      <td>[2007-01-01,2012-01-01)</td>
      <td>None</td>
      <td>20072011</td>
    </tr>
    <tr>
      <th>52</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Counties level (2008 - 2012)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_40c043db</td>
      <td>{'counts': {'rows': 3221, 'cells': 811692, 'nu...</td>
      <td>5yrs</td>
      <td>[2008-01-01,2013-01-01)</td>
      <td>None</td>
      <td>20082012</td>
    </tr>
    <tr>
      <th>53</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Counties level (2009 - 2013)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_aa75afd</td>
      <td>{'counts': {'rows': 3221, 'cells': 811692, 'nu...</td>
      <td>5yrs</td>
      <td>[2009-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20092013</td>
    </tr>
    <tr>
      <th>54</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Counties level (2010 - 2014)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_528f7e8a</td>
      <td>{'counts': {'rows': 3220, 'cells': 817880, 'nu...</td>
      <td>5yrs</td>
      <td>[2010-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>55</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Counties level (2011 - 2015)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_18e867ac</td>
      <td>{'counts': {'rows': 3220, 'cells': 798560, 'nu...</td>
      <td>5yrs</td>
      <td>[2011-01-01,2016-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>56</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Counties level (2012 - 2016)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_c6414cc6</td>
      <td>{'counts': {'rows': 3220, 'cells': 779240, 'nu...</td>
      <td>5yrs</td>
      <td>[2012-01-01,2017-01-01)</td>
      <td>None</td>
      <td>20122016</td>
    </tr>
    <tr>
      <th>57</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Counties level (2013 - 2017)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_8c2655e0</td>
      <td>{'counts': {'rows': 3220, 'cells': 811440, 'nu...</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>58</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2007)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_a0c48b07</td>
      <td>{'counts': {'rows': 788, 'cells': 198576, 'nul...</td>
      <td>yearly</td>
      <td>[2007-01-01,2008-01-01)</td>
      <td>None</td>
      <td>2007</td>
    </tr>
    <tr>
      <th>59</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2008)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_307b9696</td>
      <td>{'counts': {'rows': 790, 'cells': 199080, 'nul...</td>
      <td>yearly</td>
      <td>[2008-01-01,2009-01-01)</td>
      <td>None</td>
      <td>2008</td>
    </tr>
    <tr>
      <th>60</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2009)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_477ca600</td>
      <td>{'counts': {'rows': 792, 'cells': 199584, 'nul...</td>
      <td>yearly</td>
      <td>[2009-01-01,2010-01-01)</td>
      <td>None</td>
      <td>2009</td>
    </tr>
    <tr>
      <th>61</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2010)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_27bb2fe5</td>
      <td>{'counts': {'rows': 818, 'cells': 202046, 'nul...</td>
      <td>yearly</td>
      <td>[2010-01-01,2011-01-01)</td>
      <td>None</td>
      <td>2010</td>
    </tr>
    <tr>
      <th>62</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2011)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_50bc1f73</td>
      <td>{'counts': {'rows': 822, 'cells': 207144, 'nul...</td>
      <td>yearly</td>
      <td>[2011-01-01,2012-01-01)</td>
      <td>None</td>
      <td>2011</td>
    </tr>
    <tr>
      <th>63</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Counties (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at Counties level (2012)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_c9b54ec9</td>
      <td>{'counts': {'rows': 825, 'cells': 207900, 'nul...</td>
      <td>yearly</td>
      <td>[2012-01-01,2013-01-01)</td>
      <td>None</td>
      <td>2012</td>
    </tr>
    <tr>
      <th>64</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_2a802e0e</td>
      <td>{'counts': {'rows': 220334, 'cells': 32829766,...</td>
      <td>5yrs</td>
      <td>[2006-01-01,2011-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
    <tr>
      <th>65</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2015)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_87197151</td>
      <td>{'counts': {'rows': 52, 'cells': 12896, 'null_...</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>66</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_s...</td>
      <td>States (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>1-yr ACS data at States level (2016)</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_1e1020eb</td>
      <td>{'counts': {'rows': 52, 'cells': 12792, 'null_...</td>
      <td>yearly</td>
      <td>[2016-01-01,2017-01-01)</td>
      <td>None</td>
      <td>2016</td>
    </tr>
    <tr>
      <th>67</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_z...</td>
      <td>5-digit Zip Code Tabluation Areas (2015) - sho...</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at 5-digit Zip Code Tabluation A...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_9f1552dd</td>
      <td>{'counts': {'rows': 33120, 'cells': 8346240, '...</td>
      <td>5yrs</td>
      <td>[2008-01-01,2013-01-01)</td>
      <td>None</td>
      <td>20082012</td>
    </tr>
    <tr>
      <th>68</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_z...</td>
      <td>5-digit Zip Code Tabluation Areas (2015) - sho...</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at 5-digit Zip Code Tabluation A...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_d5724bfb</td>
      <td>{'counts': {'rows': 33120, 'cells': 8346240, '...</td>
      <td>5yrs</td>
      <td>[2009-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20092013</td>
    </tr>
    <tr>
      <th>69</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_z...</td>
      <td>5-digit Zip Code Tabluation Areas (2015) - sho...</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at 5-digit Zip Code Tabluation A...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_8d5a6f8c</td>
      <td>{'counts': {'rows': 33120, 'cells': 8412480, '...</td>
      <td>5yrs</td>
      <td>[2010-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>70</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_z...</td>
      <td>5-digit Zip Code Tabluation Areas (2015) - sho...</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at 5-digit Zip Code Tabluation A...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_c73d76aa</td>
      <td>{'counts': {'rows': 33120, 'cells': 8213760, '...</td>
      <td>5yrs</td>
      <td>[2011-01-01,2016-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>73</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_z...</td>
      <td>5-digit Zip Code Tabluation Areas (2015) - sho...</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at 5-digit Zip Code Tabluation A...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_19945dc0</td>
      <td>{'counts': {'rows': 33120, 'cells': 8015040, '...</td>
      <td>5yrs</td>
      <td>[2012-01-01,2017-01-01)</td>
      <td>None</td>
      <td>20122016</td>
    </tr>
    <tr>
      <th>74</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_z...</td>
      <td>5-digit Zip Code Tabluation Areas (2015) - sho...</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at 5-digit Zip Code Tabluation A...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_53f344e6</td>
      <td>{'counts': {'rows': 33120, 'cells': 8346240, '...</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
  </tbody>
</table>
</div>


This time, choose the block groups from ACS and check which datasets are available.

```python
datasets_df[datasets_df['id'].str.contains('blockgroup') & (datasets_df['provider_id'] == 'usa_acs')]
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>available_in</th>
      <th>category_id</th>
      <th>category_name</th>
      <th>country_id</th>
      <th>data_source_id</th>
      <th>description</th>
      <th>geography_description</th>
      <th>geography_id</th>
      <th>geography_name</th>
      <th>id</th>
      <th>...</th>
      <th>lang</th>
      <th>name</th>
      <th>provider_id</th>
      <th>provider_name</th>
      <th>slug</th>
      <th>summary_json</th>
      <th>temporal_aggregation</th>
      <th>time_coverage</th>
      <th>update_frequency</th>
      <th>version</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_b758e778</td>
      <td>{'counts': {'rows': 220333, 'cells': 36354945,...</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>14</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_31d9e865</td>
      <td>{'counts': {'rows': 220333, 'cells': 36354945,...</td>
      <td>5yrs</td>
      <td>[2009-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20092013</td>
    </tr>
    <tr>
      <th>15</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_69f1cc12</td>
      <td>{'counts': {'rows': 220333, 'cells': 36795611,...</td>
      <td>5yrs</td>
      <td>[2010-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>39</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_60e73728</td>
      <td>{'counts': {'rows': 220333, 'cells': 36354945,...</td>
      <td>5yrs</td>
      <td>[2007-01-01,2012-01-01)</td>
      <td>None</td>
      <td>20072011</td>
    </tr>
    <tr>
      <th>40</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_7bbef143</td>
      <td>{'counts': {'rows': 220333, 'cells': 36354945,...</td>
      <td>5yrs</td>
      <td>[2008-01-01,2013-01-01)</td>
      <td>None</td>
      <td>20082012</td>
    </tr>
    <tr>
      <th>41</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_2396d534</td>
      <td>{'counts': {'rows': 220333, 'cells': 36795611,...</td>
      <td>5yrs</td>
      <td>[2011-01-01,2016-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>42</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_fd3ffe5e</td>
      <td>{'counts': {'rows': 220333, 'cells': 36354945,...</td>
      <td>5yrs</td>
      <td>[2012-01-01,2017-01-01)</td>
      <td>None</td>
      <td>20122016</td>
    </tr>
    <tr>
      <th>64</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographics</td>
      <td>The American Community Survey (ACS) is an ongo...</td>
      <td>Shoreline clipped TIGER/Line boundaries. More ...</td>
      <td>carto-do-public-data.usa_carto.geography_usa_b...</td>
      <td>Census Block Groups (2015) - shoreline clipped</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>...</td>
      <td>eng</td>
      <td>5-yr ACS data at Census Block Groups level (20...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>acs_sociodemogr_2a802e0e</td>
      <td>{'counts': {'rows': 220334, 'cells': 32829766,...</td>
      <td>5yrs</td>
      <td>[2006-01-01,2011-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
  </tbody>
</table>
</div>

Nice! Let's take the first one that has aggregated data from 2013 to 2018 and check which of its variables have data about the total population.

```python
from cartoframes.data.observatory import Dataset

dataset = Dataset.get('acs_sociodemogr_b758e778')
variables_df = dataset.variables.to_dataframe()
variables_df[variables_df['description'].str.contains('total population', case=False, na=False)]
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>agg_method</th>
      <th>column_name</th>
      <th>dataset_id</th>
      <th>db_type</th>
      <th>description</th>
      <th>id</th>
      <th>name</th>
      <th>slug</th>
      <th>starred</th>
      <th>summary_json</th>
      <th>variable_group_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>116</th>
      <td>AVG</td>
      <td>income_per_capita</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>FLOAT</td>
      <td>Per Capita Income in the past 12 Months. Per c...</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>income_per_capita</td>
      <td>income_per_capi_8a9352e0</td>
      <td>None</td>
      <td>{'head': [10843, 81947, 19377, 12284, 27244, 3...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>131</th>
      <td>SUM</td>
      <td>total_pop</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>FLOAT</td>
      <td>Total Population. The total number of all peop...</td>
      <td>carto-do-public-data.usa_acs.demographics_soci...</td>
      <td>total_pop</td>
      <td>total_pop_3cf008b3</td>
      <td>None</td>
      <td>{'head': [283, 721, 421, 720, 472, 220, 387, 1...</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>

We can see the variable that contains the total population is the one with the slug `total_pop_3cf008b3`. Now we are ready to enrich our areas of influence with that variable.

```python
from cartoframes.data.observatory import Variable
from cartoframes.data.observatory import Enrichment

variable = Variable.get('total_pop_3cf008b3')

isochrones_cdf = Enrichment().enrich_polygons(isochrones_cdf, [variable])
isochrones_cdf.head()
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>source_id</th>
      <th>data_range</th>
      <th>lower_data_range</th>
      <th>the_geom</th>
      <th>range_label</th>
      <th>sum_total_pop</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-73.95933 40.68012, -73.96074 ...</td>
      <td>15 min.</td>
      <td>1238.535539</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-73.96187 40.58632, -73.96288 ...</td>
      <td>15 min.</td>
      <td>1527.769729</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-73.99081 40.62694, -73.99169 ...</td>
      <td>15 min.</td>
      <td>1406.725940</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-74.02850 40.64063, -74.02881 ...</td>
      <td>15 min.</td>
      <td>1201.498338</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-74.00110 40.60186, -74.00249 ...</td>
      <td>15 min.</td>
      <td>1414.493341</td>
    </tr>
  </tbody>
</table>
</div>

Great! Let's see the result on a map:

```python
from cartoframes.viz.helpers import color_continuous_layer

Map(color_continuous_layer(isochrones_cdf, 'sum_total_pop', 'Population'))
```

<div class="example-map">
    <iframe
        id="quickstart_guide_starbucks_brooklyn_pop"
        src="https://cartoframes.carto.com/kuviz/6dc0bf27-28f2-4d5b-93f6-acad260a0c1c"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

We can see that the area of influence of the store on the right, is the one with the highest population. Let's go a bit further and calculate and visualize the average revenue per person.

```python
stores_cdf['rev_pop'] = stores_cdf['revenue']/isochrones_cdf['sum_total_pop']
Map(size_continuous_layer(stores_cdf, 'rev_pop', 'Revenue per person ($)'))
```

<div class="example-map">
    <iframe
        id="quickstart_guide_starbucks_brooklyn_rev_pop"
        src="https://cartoframes.carto.com/kuviz/cc4e9aba-c748-48ec-84ca-55c90dfecb0f"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

As we can see, the store in the center is the one that has lower revenue per person. This insight will help us to focus on them in further analyses.

To learn more about discovering the data you want, check out the [data discovery guide](/developers/cartoframes/guides/Data-discovery). To learn more about enriching your data check out the [data enrichment guide](/developers/cartoframes/guides/Data-enrichment/).


### Publish and share your results
The final step in the workflow is to share this interactive map with your colleagues so they can explore the information on their own. Let's do it!

First, let's upload the data to CARTO to see how we can visualize CARTO tables and how it helps you to publish your maps. To upload your data, you just need to call `to_carto` from your CartoDataFrames:

```python
stores_cdf.to_carto('starbucks_stores', if_exists='replace')
isochrones_cdf.to_carto('starbucks_isochrones', if_exists='replace')
```

Now, let's visualize them and add widgets to them so people are able to see some graphs of the information and filter it. To do this, we only have to add `widget=True` to the visualization layers.


```python
result_map = Map([
    color_continuous_layer('starbucks_isochrones', 'sum_total_pop', 'Population', stroke_width=0, opacity=0.7),
    size_continuous_layer('starbucks_stores', 'rev_pop', 'Revenue per person ($)', stroke_color='white', widget=True)
])
result_map
```

<div class="example-map">
    <iframe
        id="quickstart_guide_starbucks_analysis"
        src="https://cartoframes.carto.com/kuviz/63a2cd89-a413-4b20-9cd9-e253cdc875a3"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

Cool! Now that you have a small dashboard to play with, let's publish it on CARTO so you are able to share it with anyone. To do this, you just need to call the publish method from the Map class:

```python
result_map.publish('starbucks_analysis', password=None)
```

<pre class="u-topbottom-Margin"><code>{'id': '63a2cd89-a413-4b20-9cd9-e253cdc875a3',
 'url': 'https://cartoframes.carto.com/kuviz/63a2cd89-a413-4b20-9cd9-e253cdc875a3',
 'name': 'starbucks_analysis',
 'privacy': 'link'}
</code></pre>

### Conclusion

Congratulations! You have finished this guide and have a sense about how CARTOframes can speed up your workflow. To continue learning, you can check out a specific [Guide](/developers/cartoframes/guides), the [Reference](/developers/cartoframes/reference) to know everything about a class or a method or check the [Examples](/developers/cartoframes/examples) to see CARTOframes in action.
