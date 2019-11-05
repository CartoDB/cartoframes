## Quickstart Part 1

Hi! Glad to see you made it to the Quickstart Guide! In this guide you are introduced to how CARTOframes can be used by data scientists in spatial analysis workflows. Using bike share data, this guide walks through some common steps a data scientist takes to answer the following question: **are the company's bike share stations placed in optimal locations?**

Before you get started, we encourage you to have [your environment ready](/developers/cartoframes/guides/Install-CARTOframes-in-your-Notebooks) so you can get a feel for the library by using it. If you don’t have your environment set-up yet, check out this guide first. You will need:

- A Python Notebook environment
- The CARTOframes library installed

### Spatial analysis scenario

Let's say you work for a bike share company in Arlington, Virginia and you want to better understand how your stations around the city are being used, and if these stations are placed in optimal locations.

To begin, let's outline a workflow: 

- Explore your company's data
- Discover and enrich data thanks to the CARTO catalog
- Analyse if the current bike stations are placed in optimal locations
- And finally, share the results of your analysis with your team

Let's get started!

### Explore your company's data

You will be using [this dataset](https://github.com/CartoDB/cartoframes/tree/develop/docs/developer-center/guides/data/arlington_bikeshare_july_agg.geojson) in [GeoJSON](https://geojson.org) format to start your exploration. It contains information about the bike stations around the city of Arlington. As a first exploratory step, you read it into a Jupyter Notebook using a [Geopandas GeoDataframe](http://geopandas.org/reference/geopandas.GeoDataFrame.html).

```py
import geopandas as gpd

arlington_file = 'arlington_bikeshare_july_agg.geojson'
bikeshare_df = gpd.read_file(arlington_file)
bikeshare_df.head(3)
```

<table class="dataframe" border="1">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>num_bike_dropoffs</th>
      <th>num_bike_pickups</th>
      <th>total_events</th>
      <th>station_id</th>
      <th>longitude</th>
      <th>latitude</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>178</td>
      <td>204</td>
      <td>382</td>
      <td>31000</td>
      <td>-77.053144</td>
      <td>38.858726</td>
      <td>POINT (-77.05314 38.85873)</td>
    </tr>
    <tr>
      <td>1</td>
      <td>222</td>
      <td>276</td>
      <td>498</td>
      <td>31001</td>
      <td>-77.053738</td>
      <td>38.857216</td>
      <td>POINT (-77.05374 38.85722)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>839</td>
      <td>710</td>
      <td>1549</td>
      <td>31002</td>
      <td>-77.049218</td>
      <td>38.856372</td>
      <td>POINT (-77.04922 38.85637)</td>
    </tr>
  </tbody>
</table>

By only reading the data into a geodataframe you aren't able to see at a glance where the stations are. So let's visualize it in a map!

> Note: In case your data hasn't been geocoded before, you can do it thanks to our Location Data Services. Learn how to geocode your data reading the [Data Services reference](/developers/cartoframes/reference/#heading-Data-Services).

You can visualize your geodataframes using the Map and Layer classes. You can take a look at our [reference section](/developers/cartoframes/reference/) or check the [visualization examples](/developers/cartoframes/examples/) to know all the visualization possibilities and which data sources are supported.

```py
from cartoframes.viz import Map, Layer

Map(Layer(bikeshare_df))
```

![Explore Points Layer - Bikeshare Data](../../img/guides/quickstart/explore_points_layer.png)

Great! We have a map!

Now, that you have a better sense of about where the stations are located, it's time to continue with the exploration. The next question to answer is which stations around the city are most active. To visualize this on the map, you can use a CARTOframes layer helper. Using the column `total_events`, which is the number of dropoffs and pickups at each station for the past month, let’s try a visualization helper called `size_continuous_layer` to size each station by that value:

```py
from cartoframes.viz.helpers import size_continuous_layer

Map(size_continuous_layer(bikeshare_df, 'total_events'))
```

![Explore Helper Method](../../img/guides/quickstart/explore_helper.png)

Good job! Now, just taking a look, you can see where are the stations with more activity. Also, thanks to be using a helper, we get a legend out of it.

To learn more about visualizating your data, about how to add legends, pop-ups, widgets and how to do it faster thanks to helpers, check the [visualization examples](/developers/cartoframes/examples/#example-add-default-widget).

Now, let's add another legend with the census polygons from [this dataset](https://github.com/CartoDB/cartoframes/tree/develop/docs/developer-center/guides/data/census_track.geojson):

```py
census_track = 'census_track.geojson'
census_track_df = gpd.read_file(census_track)

Map(Layer(census_track_df))
```

<table class="dataframe" border="1">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>OBJECTID</th>
      <th>FULLTRACTID</th>
      <th>TRACTID</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>1</td>
      <td>51013102901</td>
      <td>102901</td>
      <td>POLYGON ((-77.09099 38.84516, -77.08957 38.844...</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>51013103000</td>
      <td>103000</td>
      <td>POLYGON ((-77.08558 38.82992, -77.08625 38.828...</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3</td>
      <td>51013102902</td>
      <td>102902</td>
      <td>POLYGON ((-77.09520 38.84499, -77.09442 38.844...</td>
    </tr>
  </tbody>
</table>

And finally, let's combine both layers in the same visualization:

```py
Map([
    Layer(census_track_df),
    size_continuous_layer(bikeshare_df, 'total_events')
])
```

![Combine Layers](../../img/guides/quickstart/combine_layers.png)