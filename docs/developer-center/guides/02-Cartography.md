## Cartography

Map creation in cartoframes happens through the `CartoContext.map` method. This method takes a list of map layers, each with independent styling options. The layers can be a base map (`BaseMap`), table layer (`Layer`), or a query against data in the user's CARTO account (`QueryLayer`). Each of the layers is styled independently and appear on the map in the order listed. Basemaps are an exception to this ordering rule: they always appear on the bottom regardless of its order in the list.

### Base Maps

To create a map with only the `BaseMap`, do the following:

```python
from cartoframes import CartoContext, BaseMap
cc = CartoContext(
    base_url='<your_base_url>',
    api_key='<your_api_key>'
)
cc.map(layers=BaseMap())
```

Or more simply, the last line can be made simpler because a base map is added by default if one is not provided:

```python
cc.map()
```

This produces the following output:

<img src="https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers0_time0_baseid2_labels0_zoom1/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%7D&anti_cache=0.8603790764089185&zoom=1&lat=0&lon=0" />

To get a custom view, pass the longitude, latitude, and zoom as arguments to `cc.map`:

```python
cc.map(lat=34.7982209, lng=113.6489703, zoom=11)
```

To change the base map style to CARTO's 'dark matter', pass `'dark'` to the `BaseMap` class:

```python
cc.map(layers=BaseMap('dark'))
```
<img src="https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers0_time0_baseid1_labels0_zoom1/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%7D&anti_cache=0.8603790764089185&zoom=1&lat=0&lon=0" />

For a light base map, change the source to `'light'`.

<img src="https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers0_time0_baseid0_labels0_zoom1/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%7D&anti_cache=0.8603790764089185&zoom=1&lat=0&lon=0" />

Remove labels with `labels=None` or put them in back with `labels='back'`.

### Single Layer Map

To add a data layer to your map, first find a table you want to visualize.

We're going to use the NYC Taxi dataset from cartoframes examples, which you can put into your account with this snippet:

```python
from cartoframes.examples import read_taxi
# write taxi data to your account, setting the geometry as pickup location
cc.write(
    read_taxi(),
    'taxi_50k',
    lnglat=('pickup_longitude', 'pickup_latitude')
)
```

See the [cartoframes Quickstart]({{ site.url }}/documentation/cartoframes/guides/quickstart/) to cover basics used here.

```python
cc.map(layers=[
    BaseMap('dark'),
    Layer('taxi_50k', color='fare_amount')
])
```

### Map from a QueryLayer

Maps can be created from arbitrary queries of tables you have in your account. With our example taxi dataset, you may have noticed that there are two sets of long/lat coordinates: one for pickup location, another for dropoff location. We can use this information to draw a straight-line path and get this length. Of course, the real route would be more useful, but this isn't in the data. We could simulate it with CARTO's routing functions, but we'll stick with the simpler example of straight-line paths for demonstration.

In this example, you'll notice a few features:

1. The line geometry is created with the PostGIS functions `ST_MakeLine` from points created with the cartodb-postgresql helper function `CDB_LatLng`](https://github.com/CartoDB/cartodb-postgresql/blob/master/scripts-available/CDB_LatLng.sql)
2. We filter out locations at lnt/lat (0, 0) which are from null values
3. We order by the distance (fourth in the SELECT) to make sure the shortest paths are drawn on top and not obscured by longer paths
4. Color by the distance between the pick up and drop off locations
5. Zoom into a location of interest

```python
from cartoframes import QueryLayer
cc.map(
    QueryLayer('''
        SELECT
            ST_Transform(the_geom, 3857) AS the_geom_webmercator,
            the_geom,
            cartodb_id,
            ST_Length(the_geom::geography) AS distance
        FROM (
            SELECT
                ST_MakeLine(
                    CDB_LatLng(pickup_latitude, pickup_longitude),
                    CDB_LatLng(dropoff_latitude, dropoff_longitude)
                ) AS the_geom,
                cartodb_id
            FROM taxi_50k
            WHERE pickup_latitude <> 0 AND dropoff_latitude <> 0
        ) AS _w
        ORDER BY 4 DESC''',
        color='distance'),
    zoom=11, lng=-73.9442, lat=40.7473,
    interactive=False)
```

<img src="https://eschbacher.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers1_time0_baseid2_labels1_zoom1/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_nolabels%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer+%7B++line-width%3A+1.5%3B+line-color%3A+ramp%28%5Bdistance%5D%2C+cartocolor%28Sunset%29%2C+quantiles%287%29%2C+%3E%29%3B%7D%23layer%5Bdistance+%3D+null%5D+%7B++line-color%3A+%23ccc%3B%7D%22%2C+%22sql_0%22%3A+%22%5Cn++++SELECT%5Cn++++++++ST_Transform%28the_geom%2C+3857%29+as+the_geom_webmercator%2C%5Cn++++++++the_geom%2C%5Cn++++++++cartodb_id%2C%5Cn++++++++ST_Length%28the_geom%3A%3Ageography%29+as+distance%5Cn++++FROM+%28%5Cn++++++++SELECT%5Cn++++++++++++ST_MakeLine%28%5Cn++++++++++++++++CDB_LatLng%28pickup_latitude%2C+pickup_longitude%29%2C%5Cn++++++++++++++++CDB_LatLng%28dropoff_latitude%2C+dropoff_longitude%29%5Cn++++++++++++%29+as+the_geom%2C%5Cn++++++++++++cartodb_id%5Cn++++++++FROM+taxi_50k%5Cn++++++++WHERE+pickup_latitude+%3C%3E+0+and+dropoff_latitude+%3C%3E+0%5Cn++++%29+as+_w%5Cn++++ORDER+BY+4+desc%5Cn%22%7D&anti_cache=0.114623178036098&zoom=13&lat=40.7207&lon=-73.9782" />

`QueryLayer`s are a great way to take advantage of the relational database underlying CARTO without creating new datasets. For resource-intensive operations, it is recommended to first create a new dataset for visualization with `Layer` as it will offer better performance and be less likely to hit platform limits. To create new tables from queries, use `CartoContext.query('<query>', table_name='<new_table_name>')`.

### Multi-layer Map

To add more than one layer to your map, add them in the order you want the layers to display. Here we're adding a base map using a light styling, a polygon layer of poverty rates in Brooklyn, and the taxi data for fares above $50 sized by the amount.

```python
cc.map(layers=[
    BaseMap('light'),
    Layer('brooklyn_poverty', color='poverty_per_pop'),
    QueryLayer(
        'SELECT * FROM taxi_50k WHERE fare_amount > 50',
        size='fare_amount'
    )
])
```

<img src="https://eschbacher.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers2_time0_baseid0_labels0_zoom0/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Flight_all%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer+%7B++polygon-fill%3A+ramp%28%5Bpoverty_per_pop%5D%2C+cartocolor%28Mint%29%2C+quantiles%285%29%2C+%3E%29%3B+polygon-opacity%3A+0.9%3B+polygon-gamma%3A+0.5%3B+line-color%3A+%23FFF%3B+line-width%3A+0.5%3B+line-opacity%3A+0.25%3B+line-comp-op%3A+hard-light%3B%7D%23layer%5Bpoverty_per_pop+%3D+null%5D+%7B++polygon-fill%3A+%23ccc%3B%7D%22%2C+%22sql_0%22%3A+%22SELECT+%2A+FROM+brooklyn_poverty%22%2C+%22cartocss_1%22%3A+%22%23layer+%7B++marker-width%3A+ramp%28%5Bfare_amount%5D%2C+range%285%2C25%29%2C+quantiles%285%29%29%3B+marker-fill%3A+%23f3e79b%3B+marker-fill-opacity%3A+1%3B+marker-allow-overlap%3A+true%3B+marker-line-width%3A+0.5%3B+marker-line-color%3A+%23FFF%3B+marker-line-opacity%3A+1%3B%7D%22%2C+%22sql_1%22%3A+%22SELECT+%2A+FROM+taxi_50k+WHERE+fare_amount+%3E+50%22%7D&anti_cache=0.31948174709555843&bbox=-74.6638793945312%2C40.569596%2C-73.6438598632812%2C40.8840484619141" />

### Style Size by Variable

To style by size variable, use the `size` keyword at the layer level for each layer passed. This only work for point data.

This sizes each point the same size (3 pixels wide):

```python
cc.map(layers=Layer('taxi_50k', size=3))
```

To size by a variable, pass a column name instead of a number:

```python
cc.map(
    layers=Layer(
        'taxi_50k',
        size='fare_amount'
    ))
```

Just like the `color` keyword, the size option can take a dictionary. 

```python
cc.map(
    layers=Layer(
        'taxi_50k',
        size={
            'column': 'fare_amount',
            'min': 2,
            'max': 10,
            'bin_method': 'headtails'
        }
    )
)
```

Your results will look as follows:

<img src="https://eschbacher.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers1_time0_baseid2_labels0_zoom1/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer+%7B++marker-width%3A+ramp%28%5Bfare_amount%5D%2C+range%282%2C10%29%2C+headtails%285%29%29%3B+marker-fill%3A+%235D69B1%3B+marker-fill-opacity%3A+1%3B+marker-allow-overlap%3A+true%3B+marker-line-width%3A+0.5%3B+marker-line-color%3A+%23FFF%3B+marker-line-opacity%3A+1%3B%7D%22%2C+%22sql_0%22%3A+%22SELECT+%2A+FROM+taxi_50k%22%7D&anti_cache=0.6669375663279264&zoom=14&lat=40.7366&lon=-73.9885" />

### Style Color by Variable

Styling values by color is similar to styling by size but using the `color` keyword in the Layer object instead. Color by value works for points, lines, and polygons.

Using the `brooklyn_poverty` dataset, we can style by `poverty_per_pop`:

```python
from cartofrmaes import Layer
cc.map(Layer('brooklyn_poverty', color='poverty_per_pop'))
```

To specify a specific color scheme, we can expand the argument to color and using some of the color utility functions in the `styling` module:

```python
from cartoframes import Layer, styling
cc.map(
    Layer(
        'brooklyn_poverty',
        color={'column': 'poverty_per_pop',
               'scheme': styling.sunset(7)}
    )
)
```

### Animated Map

To style a map with time, use the `time` keyword on a numeric or time field in your dataset. Here we use the US Geological Survey [data feed](https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv) on earthquakes which has a `time` column.

To get this data into your CARTO account with CARTOframes, do the following:

```python
import pandas as pd
eq_url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv'
cc.write(pd.read_csv(eq_url), 'usgs_all_month')
```

To visualize the data in time, specify the column that has the time information (in this case `time`). We can also style by color. Here we're using the `net` column which is a category.
```python
cc.map(Layer('usgs_all_month', time='time', color='net'))
```
