
# Basic cartoframes usage

`cartoframes` lets you use CARTO in a Python environment so that you can do all of your analysis and mapping in, for example, a Jupyter notebook. `cartoframes` allows you to use CARTO's functionality for data analysis, storage, location services like routing and geocoding, and visualization.

You can view this notebook best on `nbviewer` here: <https://nbviewer.jupyter.org/github/CartoDB/cartoframes/blob/master/examples/Basic%20Usage.ipynb>
It is recommended to download this notebook and use on your computer instead so you can more easily explore the functionality of `cartoframes`.

To get started, let's load the required packages, and set credentials.


```python
%matplotlib inline
import cartoframes
from cartoframes import Credentials
import pandas as pd

USERNAME = 'eschbacher'  # <-- replace with your username 
APIKEY = 'abcdefg'       # <-- your CARTO API key
creds = Credentials(username=USERNAME, 
                    key=APIKEY)
cc = cartoframes.CartoContext(creds=creds)
```

## `cc.read`

`CartoContext` has several methods for interacting with [CARTO](https://carto.com) in a Python environment. `CartoContext.read` allows you to pull a dataset stored on CARTO into a [pandas](http://pandas.pydata.org/) DataFrame. In the cell below, we use `cc.read` to get the table `brooklyn_poverty` from a CARTO account. You can get a CSV of the table here for uploading to your CARTO account:

<https://cartoframes.carto.com/api/v2/sql?q=SELECT+*+FROM+brooklyn_poverty&format=csv&filename=brooklyn_poverty>


```python
# Get a CARTO table as a pandas DataFrame
df = cc.read('brooklyn_poverty')
df.head()
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>commuters_16_over_2011_2015</th>
      <th>geoid</th>
      <th>pop_determined_poverty_status_2011_2015</th>
      <th>poverty_count</th>
      <th>poverty_per_pop</th>
      <th>the_geom</th>
      <th>the_geom_webmercator</th>
      <th>total_pop_2011_2015</th>
      <th>total_population</th>
      <th>walked_to_work_2011_2015</th>
    </tr>
    <tr>
      <th>cartodb_id</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2</th>
      <td>4074.192637</td>
      <td>360470050003</td>
      <td>3304.439797</td>
      <td>23.112583</td>
      <td>0.031191</td>
      <td>0103000020E6100000010000000B0000006D3A02B85982...</td>
      <td>0103000020110F0000010000000B000000D240DAA89070...</td>
      <td>9624.365242</td>
      <td>741</td>
      <td>0.005207</td>
    </tr>
    <tr>
      <th>585</th>
      <td>5434.149852</td>
      <td>360470218001</td>
      <td>27809.352304</td>
      <td>770.733564</td>
      <td>0.250000</td>
      <td>0103000020E6100000010000000B000000ACE3F8A1D27F...</td>
      <td>0103000020110F0000010000000B0000000354CD84456C...</td>
      <td>16072.338976</td>
      <td>756</td>
      <td>0.042990</td>
    </tr>
    <tr>
      <th>15</th>
      <td>32412.498980</td>
      <td>360470514002</td>
      <td>39958.419065</td>
      <td>574.101597</td>
      <td>0.325824</td>
      <td>0103000020E610000001000000070000003DB5FAEAAA7D...</td>
      <td>0103000020110F00000100000007000000ADF228609C68...</td>
      <td>61660.046010</td>
      <td>1762</td>
      <td>0.008740</td>
    </tr>
    <tr>
      <th>16</th>
      <td>5135.760974</td>
      <td>360470534003</td>
      <td>23191.290336</td>
      <td>235.858921</td>
      <td>0.391142</td>
      <td>0103000020E61000000100000008000000EBABAB02B57D...</td>
      <td>0103000020110F000001000000080000008ECED184AD68...</td>
      <td>14912.553653</td>
      <td>603</td>
      <td>0.016081</td>
    </tr>
    <tr>
      <th>146</th>
      <td>486.050087</td>
      <td>360470013002</td>
      <td>8739.299360</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0103000020E6100000010000001500000005854199467F...</td>
      <td>0103000020110F000001000000150000003D6926A8576B...</td>
      <td>40739.834591</td>
      <td>939</td>
      <td>0.037871</td>
    </tr>
  </tbody>
</table>
</div>



Notice that:

* the index of the DataFrame is the same as the index of the CARTO table (`cartodb_id`)
* `the_geom` column stores the geometry. This can be decoded if we set the `decode_geom=True` flag in `cc.read`, which requires the library `shapely`.
* We have several numeric columns
* SQL `null` values are represented as `np.nan`

Other things to notice:


```python
df.dtypes
```




    commuters_16_over_2011_2015                float64
    geoid                                       object
    pop_determined_poverty_status_2011_2015    float64
    poverty_count                              float64
    poverty_per_pop                            float64
    the_geom                                    object
    the_geom_webmercator                        object
    total_pop_2011_2015                        float64
    total_population                             int64
    walked_to_work_2011_2015                   float64
    dtype: object



The `dtype` of each column is a mapping of the column type on CARTO. For example, `numeric` will map to `float64`, `text` will map to `object` (pandas string representation), `timestamp` will map to `datetime64[ns]`, etc. The reverse happens if a DataFrame is sent to CARTO.

## `cc.map`

Now that we can inspect the data, we can map it to see how the values change over the geography. We can use the `cc.map` method for this purpose.

`cc.map` takes a `layers` argument which specifies the data layers that are to be visualized. They can be imported from `cartoframes` as below.

There are different types of layers:

* `Layer` for visualizing CARTO tables
* `QueryLayer` for visualizing arbitrary queries from tables in user's CARTO account
* `BaseMap` for specifying the base map to be used

Each of the layers has different styling options. `Layer` and `QueryLayer` take the same styling arguments, and `BaseMap` can be specified to be light/dark and options on label placement.

Maps can be `interactive` or not. Set interactivity with the `interactive` with `True` or `False`. If the map is static (not interactive), it will be embedded in the notebook as either a `matplotlib` axis or `IPython.Image`. Either way, the image will be transported with the notebook. Interactive maps will be embedded zoom and pan-able maps.


```python
from cartoframes import Layer, styling
l = Layer('brooklyn_poverty',
          color={'column': 'poverty_per_pop',
                 'scheme': styling.sunset(7)})
cc.map(layers=l,
       interactive=False)
```




    <matplotlib.axes._subplots.AxesSubplot at 0x113361160>




![png](./docs/examples/BasicUseage_files/./docs/examples/BasicUseage_8_1.png)


## NYC Taxi Dataset

Let's explore a typical `cartoframes` workflow using data on NYC taxis.

To get the data into CARTO, we can:
1. Use `pandas` to grab the data from the cartoframes example account
2. Send it to your CARTO account using `cc.write`, specifying the `lng`/`lat` columns you want to use for visualization
3. Set `overwrite=True` to replace an existing dataset if it exists
4. Refresh our `df` with the CARTO-fied version using `cc.read``


```python
# read in a CSV of NYC taxi data from cartoframes example datasets
df = pd.read_csv('https://cartoframes.carto.com/api/v2/sql?q=SELECT+*+FROM+taxi_50k&format=csv')

# set the index of the dataframe to be the cartodb_id (database index)
df.set_index('cartodb_id', inplace=True)

# show first five rows to see what we've got
df.head()
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>the_geom</th>
      <th>the_geom_webmercator</th>
      <th>vendorid</th>
      <th>tpep_pickup_datetime</th>
      <th>tpep_dropoff_datetime</th>
      <th>passenger_count</th>
      <th>trip_distance</th>
      <th>pickup_longitude</th>
      <th>pickup_latitude</th>
      <th>ratecodeid</th>
      <th>...</th>
      <th>dropoff_longitude</th>
      <th>dropoff_latitude</th>
      <th>payment_type</th>
      <th>fare_amount</th>
      <th>extra</th>
      <th>mta_tax</th>
      <th>tip_amount</th>
      <th>tolls_amount</th>
      <th>improvement_surcharge</th>
      <th>total_amount</th>
    </tr>
    <tr>
      <th>cartodb_id</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>2</td>
      <td>2016-05-01 14:52:11+00</td>
      <td>2016-05-01 15:00:36+00</td>
      <td>2</td>
      <td>2.08</td>
      <td>-74.006706</td>
      <td>40.730461</td>
      <td>1</td>
      <td>...</td>
      <td>-74.012383</td>
      <td>40.706779</td>
      <td>1</td>
      <td>8.5</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>1.00</td>
      <td>0.0</td>
      <td>0.3</td>
      <td>10.30</td>
    </tr>
    <tr>
      <th>2</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>1</td>
      <td>2016-05-01 08:34:08+00</td>
      <td>2016-05-01 08:49:02+00</td>
      <td>1</td>
      <td>3.00</td>
      <td>-73.924957</td>
      <td>40.744125</td>
      <td>1</td>
      <td>...</td>
      <td>-73.973824</td>
      <td>40.762779</td>
      <td>1</td>
      <td>13.5</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>2.00</td>
      <td>0.0</td>
      <td>0.3</td>
      <td>16.30</td>
    </tr>
    <tr>
      <th>3</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>1</td>
      <td>2016-05-04 09:44:40+00</td>
      <td>2016-05-04 10:07:09+00</td>
      <td>1</td>
      <td>2.10</td>
      <td>-73.973488</td>
      <td>40.748501</td>
      <td>1</td>
      <td>...</td>
      <td>-73.998955</td>
      <td>40.740833</td>
      <td>2</td>
      <td>14.5</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>0.00</td>
      <td>0.0</td>
      <td>0.3</td>
      <td>15.30</td>
    </tr>
    <tr>
      <th>4</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>2</td>
      <td>2016-05-01 20:50:11+00</td>
      <td>2016-05-01 21:05:24+00</td>
      <td>1</td>
      <td>4.41</td>
      <td>-73.999786</td>
      <td>40.743267</td>
      <td>1</td>
      <td>...</td>
      <td>-73.966362</td>
      <td>40.792370</td>
      <td>2</td>
      <td>15.0</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>0.00</td>
      <td>0.0</td>
      <td>0.3</td>
      <td>16.30</td>
    </tr>
    <tr>
      <th>5</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>2</td>
      <td>2016-05-02 07:26:56+00</td>
      <td>2016-05-02 07:53:53+00</td>
      <td>2</td>
      <td>4.01</td>
      <td>-73.963631</td>
      <td>40.803360</td>
      <td>1</td>
      <td>...</td>
      <td>-73.956963</td>
      <td>40.784939</td>
      <td>1</td>
      <td>19.5</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>4.06</td>
      <td>0.0</td>
      <td>0.3</td>
      <td>24.36</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 21 columns</p>
</div>




```python
# send it to carto so we can map it
# specify the columns we want to have as a point (pickup location)
cc.write(df, 'taxi_50k',
         lnglat=('pickup_longitude', 'pickup_latitude'),
         overwrite=True)

# read the fresh carto-fied version
df = cc.read('taxi_50k')
```

    Creating geometry out of columns `pickup_longitude`/`pickup_latitude`
    Table successfully written to CARTO: https://eschbacher.carto.com/dataset/taxi_50k


Take a look at the data on a map.


```python
from cartoframes import Layer
cc.map(layers=Layer('taxi_50k'),
       interactive=False)
```




    <matplotlib.axes._subplots.AxesSubplot at 0x1133b4780>




![png](./docs/examples/BasicUseage_files/./docs/examples/BasicUseage_13_1.png)


Oops, there are some zero-valued long/lats in there, so the results are going to [null island](https://en.wikipedia.org/wiki/Null_Island). Let's remove them.


```python
# select only the rows which are not at (0,0)
df = df[(df['pickup_longitude'] != 0) | (df['pickup_latitude'] != 0)]
# send back up to CARTO
cc.write(df, 'taxi_50k', overwrite=True,
         lnglat=('pickup_longitude', 'pickup_latitude'))
```

    Creating geometry out of columns `pickup_longitude`/`pickup_latitude`
    Table successfully written to CARTO: https://eschbacher.carto.com/dataset/taxi_sample



```python
# Let's take a look at what's going on, styled by the fare amount
cc.map(layers=Layer('taxi_sample',
                    size=4,
                    color={'column': 'fare_amount',
                           'scheme': styling.sunset(7)}),
       interactive=True)
```




<iframe srcdoc="<!DOCTYPE html>
<html>
  <head>
    <title>Carto</title>
    <meta name='viewport' content='initial-scale=1.0, user-scalable=no' />
    <meta http-equiv='content-type' content='text/html; charset=UTF-8' />
    <link rel='shortcut icon' href='http://cartodb.com/assets/favicon.ico' />

    <style>
     html, body, #map {
       height: 100%;
       padding: 0;
       margin: 0;
     }
     #zoom-center {
       position: absolute;
       right: 0;
       top: 0;
       background-color: rgba(255, 255, 255, 0.7);
       width: 240px;
       z-index: 100;
       padding: 4px;
     }
    </style>

    <link rel='stylesheet' href='https://cartodb-libs.global.ssl.fastly.net/cartodb.js/v3/3.15/themes/css/cartodb.css' />
  </head>
  <body>
    <div id='zoom-center'>
      zoom=<span id='zoom'>4</span>,
      lng=<span id='lon'>No data</span>, lat=<span id='lat'>No data</span></div>
    <div id='map'></div>
    <script src='https://cartodb-libs.global.ssl.fastly.net/cartodb.js/v3/3.15/cartodb.js'></script>

    <script>
     const config  = {&quot;user_name&quot;: &quot;eschbacher&quot;, &quot;maps_api_template&quot;: &quot;https://eschbacher.carto.com&quot;, &quot;sql_api_template&quot;: &quot;https://eschbacher.carto.com&quot;, &quot;tiler_protocol&quot;: &quot;https&quot;, &quot;tiler_domain&quot;: &quot;carto.com&quot;, &quot;tiler_port&quot;: &quot;80&quot;, &quot;type&quot;: &quot;namedmap&quot;, &quot;named_map&quot;: {&quot;name&quot;: &quot;cartoframes_ver20170406_layers1_time0_baseid1_labels0_zoom0&quot;, &quot;params&quot;: {&quot;basemap_url&quot;: &quot;https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png&quot;, &quot;cartocss_0&quot;: &quot;#layer[&#92;'mapnik::geometry_type&#92;'=1] {  marker-width: 4; marker-fill: ramp([fare_amount], cartocolor(Sunset), quantiles(7)); marker-fill-opacity: 1; marker-allow-overlap: true; marker-line-width: 0.5; marker-line-color: #000; marker-line-opacity: 1;} #layer[&#92;'mapnik::geometry_type&#92;'=2] {  line-width: 1.5; line-color: ramp([fare_amount], cartocolor(Sunset), quantiles(7));} #layer[&#92;'mapnik::geometry_type&#92;'=3] {  polygon-fill: ramp([fare_amount], cartocolor(Sunset), quantiles(7)); polygon-opacity: 0.9; polygon-gamma: 0.5; line-color: #FFF; line-width: 0.5; line-opacity: 0.25; line-comp-op: hard-light;} &quot;, &quot;sql_0&quot;: &quot;SELECT * FROM taxi_sample&quot;, &quot;west&quot;: -74.6638793945312, &quot;south&quot;: 40.5904769897461, &quot;east&quot;: -73.5582504272461, &quot;north&quot;: 41.1549949645996}}};
     const bounds  = [[41.1549949645996, -73.5582504272461], [40.5904769897461, -74.6638793945312]];
     const options = {&quot;filter&quot;: [&quot;http&quot;, &quot;mapnik&quot;, &quot;torque&quot;], &quot;https&quot;: true};

     const adjustLongitude = (lng) => (
       lng - ((Math.ceil((lng + 180) / 360) - 1) * 360)
     );
     const map = L.map('map', {
       zoom: 3,
       center: [0, 0],
     });
     const updateMapInfo = () => {
       $('#zoom').text(map.getZoom());
       $('#lat').text(map.getCenter().lat.toFixed(4));
       $('#lon').text(adjustLongitude(map.getCenter().lng).toFixed(4));
     };

     cartodb.createLayer(map, config, options)
            .addTo(map)
            .done((layer) => {
              if (bounds.length) {
                map.fitBounds(bounds);
              }
              updateMapInfo();
              map.on('move', () => {
                updateMapInfo();
              });
            })
            .error((err) => {
              console.log('ERROR: ', err);
            });
    </script>

  </body>
</html>
" width=800 height=400>  Preview image: <img src="https://eschbacher.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers1_time0_baseid1_labels0_zoom0/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2Fcartodb-basemaps-%7Bs%7D.global.ssl.fastly.net%2Fdark_all%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%2C+%22cartocss_0%22%3A+%22%23layer%5B%27mapnik%3A%3Ageometry_type%27%3D1%5D+%7B++marker-width%3A+4%3B+marker-fill%3A+ramp%28%5Bfare_amount%5D%2C+cartocolor%28Sunset%29%2C+quantiles%287%29%29%3B+marker-fill-opacity%3A+1%3B+marker-allow-overlap%3A+true%3B+marker-line-width%3A+0.5%3B+marker-line-color%3A+%23000%3B+marker-line-opacity%3A+1%3B%7D+%23layer%5B%27mapnik%3A%3Ageometry_type%27%3D2%5D+%7B++line-width%3A+1.5%3B+line-color%3A+ramp%28%5Bfare_amount%5D%2C+cartocolor%28Sunset%29%2C+quantiles%287%29%29%3B%7D+%23layer%5B%27mapnik%3A%3Ageometry_type%27%3D3%5D+%7B++polygon-fill%3A+ramp%28%5Bfare_amount%5D%2C+cartocolor%28Sunset%29%2C+quantiles%287%29%29%3B+polygon-opacity%3A+0.9%3B+polygon-gamma%3A+0.5%3B+line-color%3A+%23FFF%3B+line-width%3A+0.5%3B+line-opacity%3A+0.25%3B+line-comp-op%3A+hard-light%3B%7D+%22%2C+%22sql_0%22%3A+%22SELECT+%2A+FROM+taxi_sample%22%7D&anti_cache=0.4087411077898607" /></iframe>



We can use the `zoom=..., lng=..., lat=...` information in the embedded interactive map to help us get static snapshots of the regions we're interested in. For example, JFK airport is around `zoom=12, lng=-73.7880, lat=40.6629`. We can paste that information as arguments in `cc.map` to generate a static snapshot of the data there.


```python
# Let's take a look at what's going on at JFK airport, styled by the fare amount, and STATIC
cc.map(layers=Layer('taxi_sample',
                    size=4,
                    color={'column': 'fare_amount',
                           'scheme': styling.sunset(7)}),
       zoom=12, lng=-73.7880, lat=40.6629,
       interactive=False)
```




    <matplotlib.axes._subplots.AxesSubplot at 0x119c01240>




![png](./docs/examples/BasicUseage_files/./docs/examples/BasicUseage_18_1.png)

