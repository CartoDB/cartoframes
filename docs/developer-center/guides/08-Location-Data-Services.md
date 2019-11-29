## Location Data Services

### Introduction

CARTOframes provides the functionality of using the [CARTO Data Services API](https://carto.com/developers/data-services-api/). This API consists of a set of location based functions that can be applied to your data in order to perform geospatial analyses without leaving the context of your notebook.

For instance, you can **geocode** a pandas DataFrame with addresses on the fly, and then perform trade areas analysis by computing **isodistances** or **isochrones** programatically.

In this guide we go through the use case of, given a set of ten Starbucks store addresses, finding good location candidates to open another store.

> Based on your account plan, some of these location data services are subject to different [quota limitations](https://carto.com/developers/data-services-api/support/quota-information/)

### Data

We will be using the same dataset of fake locations used along these guides [starbucks_brooklyn.csv](https://github.com/CartoDB/cartoframes/blob/develop/examples/files/starbucks_brooklyn.csv)

### Authentication

Using Location Data Services requires to be authenticated. For more information about how to authenticate, please read the [Login to CARTO Platform guide](/developers/cartoframes/guides/Authentication/)

```python
from cartoframes.auth import Credentials, set_default_credentials

set_default_credentials('creds.json')
```

### Geocoding

The first step is to read and understand the data we have. Once we've the Starbucks store data in a DataFrame, we can see we've two columns that can be used in the **geocoding** service: `name` and `address`. There's also a third column that reflects the anual revenue of the store.

```python
import pandas

df = pandas.read_csv('../files/starbucks_brooklyn.csv')
df
```

<div>
<table class="dataframe">
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
      <td>1.321041e+06</td>
    </tr>
    <tr>
      <th>1</th>
      <td>607 Brighton Beach Ave</td>
      <td>607 Brighton Beach Avenue,Brooklyn, NY 11235</td>
      <td>1.268080e+06</td>
    </tr>
    <tr>
      <th>2</th>
      <td>65th St &amp; 18th Ave</td>
      <td>6423 18th Avenue,Brooklyn, NY 11204</td>
      <td>1.248134e+06</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Bay Ridge Pkwy &amp; 3rd Ave</td>
      <td>7419 3rd Avenue,Brooklyn, NY 11209</td>
      <td>1.185703e+06</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Caesar's Bay Shopping Center</td>
      <td>8973 Bay Parkway,Brooklyn, NY 11214</td>
      <td>1.148427e+06</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Court St &amp; Dean St</td>
      <td>167 Court Street,Brooklyn, NY 11201</td>
      <td>1.144067e+06</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Target Gateway T-1401</td>
      <td>519 Gateway Dr,Brooklyn, NY 11239</td>
      <td>1.021083e+06</td>
    </tr>
    <tr>
      <th>7</th>
      <td>3rd Ave &amp; 92nd St</td>
      <td>9202 Third Avenue,Brooklyn, NY 11209</td>
      <td>9.257073e+05</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Lam Group @ Sheraton Brooklyn</td>
      <td>228 Duffield st,Brooklyn, NY 11201</td>
      <td>7.657935e+05</td>
    </tr>
    <tr>
      <th>9</th>
      <td>33-42 Hillel Place</td>
      <td>33-42 Hillel Place,Brooklyn, NY 11210</td>
      <td>7.492163e+05</td>
    </tr>
  </tbody>
</table>
</div>

#### Quota consumption

Each time you run a Location Data Service, you're consuming quota. For this reason, we provide the hability to check in advance the **amount of credits** this operation will consume by using the `dry_run` parameter when running the service function.

Also, it is possible to check the available quota by running the `available_quota` function.

```python
from cartoframes.data.services import Geocoding

geo_service = Geocoding()

_, geo_dry_metadata = geo_service.geocode(
    df,
    street='address',
    city={'value': 'New York'},
    country={'value': 'USA'},
    dry_run=True
)
```

```python
geo_dry_metadata
```

```
{'total_rows': 10,
  'required_quota': 10,
  'previously_geocoded': 0,
  'previously_failed': 0,
  'records_with_geometry': 0}
```

```python
geo_service.available_quota()
```

```
1470
```

```python
geo_cdf, geo_metadata = geo_service.geocode(
    df,
    street='address',
    city={'value': 'New York'},
    country={'value': 'USA'}
)
```

If the CSV file should ever change, cached results will only be applied to unmodified
records, and new geocoding will be performed only on new or changed records.

In order to be able to use cached results, we have to save the results in a CARTO table using `table_name` and `cached=True` parameters.

```python
geo_cdf, geo_metadata = geo_service.geocode(
    df,
    street='address',
    city={'value': 'New York'},
    country={'value': 'USA'},
    table_name='starbucks_cache',
    cached=True
)
```

Let's compare the `geo_dry_metadata` and the `geo_metadata` to see the differences between the information when using or not the `dry_run` option. As we can see, this information reflects that all the locations have been geocoded successfully and that it has consumed 10 credits of quota.

```python
geo_metadata
```

```
{'total_rows': 10,
  'required_quota': 10,
  'previously_geocoded': 0,
  'previously_failed': 0,
  'records_with_geometry': 0,
  'final_records_with_geometry': 10,
  'geocoded_increment': 10,
  'successfully_geocoded': 10,
  'failed_geocodings': 0}
```

The resulting data is a `CartoDataFrame` that contains three new columns:

* `geometry`: The resulting geometry
* `gc_status_rel`: The percentage of accuracy of each location
* `carto_geocode_hash`: Geocode information

```python
geo_cdf.head()
```

<div>
<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>address</th>
      <th>revenue</th>
      <th>gc_status_rel</th>
      <th>carto_geocode_hash</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Franklin Ave &amp; Eastern Pkwy</td>
      <td>341 Eastern Pkwy,Brooklyn, NY 11238</td>
      <td>1321040.772</td>
      <td>0.97</td>
      <td>c834a8e289e5bce280775a9bf1f833f1</td>
      <td>POINT (-73.95901 40.67109)</td>
    </tr>
    <tr>
      <th>2</th>
      <td>607 Brighton Beach Ave</td>
      <td>607 Brighton Beach Avenue,Brooklyn, NY 11235</td>
      <td>1268080.418</td>
      <td>0.99</td>
      <td>7d39a3fff93efd9034da88aa9ad2da79</td>
      <td>POINT (-73.96122 40.57796)</td>
    </tr>
    <tr>
      <th>3</th>
      <td>65th St &amp; 18th Ave</td>
      <td>6423 18th Avenue,Brooklyn, NY 11204</td>
      <td>1248133.699</td>
      <td>0.98</td>
      <td>1a2312049ddea753ba42bf77f5ccf718</td>
      <td>POINT (-73.98976 40.61912)</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Bay Ridge Pkwy &amp; 3rd Ave</td>
      <td>7419 3rd Avenue,Brooklyn, NY 11209</td>
      <td>1185702.676</td>
      <td>0.98</td>
      <td>827ab4dcc2d49d5fd830749597976d4a</td>
      <td>POINT (-74.02744 40.63152)</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Caesar's Bay Shopping Center</td>
      <td>8973 Bay Parkway,Brooklyn, NY 11214</td>
      <td>1148427.411</td>
      <td>0.98</td>
      <td>119a38c7b51195cd4153fc81605a8495</td>
      <td>POINT (-74.00098 40.59321)</td>
    </tr>
  </tbody>
</table>
</div>

In addition, to prevent having to geocode records that have been **previously geocoded**, and thus spend quota **unnecessarily**, you should always preserve the ``the_geom`` and ``carto_geocode_hash`` columns generated by the geocoding process.

This will happen **automatically** in these cases:

1. Your input is a **table** from CARTO processed in place (without a ``table_name`` parameter)
2. If you save your results in a CARTO table using the ``table_name`` parameter, and only use the resulting table for any further geocoding.

If try to geocode now this DataFrame, which contains both ``the_geom`` and the ``carto_geocode_hash``, we can see that the required quota is 0 cause it has already been geocoded.

```python
_, repeat_geo_metadata = geo_service.geocode(
    geo_cdf,
    street='address',
    city={'value': 'New York'},
    country={'value': 'USA'},
    dry_run=True
)

repeat_geo_metadata.get('required_quota')
```

```
0
```

#### Precision

The `address` column is more complete than the `name` column, and therefore, the resulting coordinates calculated by the service will be more accurate. If we check this, the accuracy values using the `name` column (`0.95, 0.93, 0.96, 0.83, 0.78, 0.9`) are lower than the ones we get by using the `address` column for geocoding (`0.97, 0.99, 0.98`)

```python
geo_name_cdf, geo_name_metadata = geo_service.geocode(
    df,
    street='name',
    city={'value': 'New York'},
    country={'value': 'USA'}
)
```

```python
geo_name_cdf.head()
```

<div>
<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>address</th>
      <th>revenue</th>
      <th>gc_status_rel</th>
      <th>carto_geocode_hash</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Franklin Ave &amp; Eastern Pkwy</td>
      <td>341 Eastern Pkwy,Brooklyn, NY 11238</td>
      <td>1321040.772</td>
      <td>0.95</td>
      <td>0be7693fc688eca36e1077656dcb00a5</td>
      <td>POINT (-76.56478 39.30853)</td>
    </tr>
    <tr>
      <th>2</th>
      <td>607 Brighton Beach Ave</td>
      <td>607 Brighton Beach Avenue,Brooklyn, NY 11235</td>
      <td>1268080.418</td>
      <td>0.95</td>
      <td>084a5c4d42ccf3c3c8e69426619f270e</td>
      <td>POINT (-73.96122 40.57796)</td>
    </tr>
    <tr>
      <th>3</th>
      <td>65th St &amp; 18th Ave</td>
      <td>6423 18th Avenue,Brooklyn, NY 11204</td>
      <td>1248133.699</td>
      <td>0.93</td>
      <td>1d9a17c20c11d0454aff10548a328c47</td>
      <td>POINT (-73.99018 40.61914)</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Bay Ridge Pkwy &amp; 3rd Ave</td>
      <td>7419 3rd Avenue,Brooklyn, NY 11209</td>
      <td>1185702.676</td>
      <td>0.96</td>
      <td>d531df27fc02336dc722cb4e7028b244</td>
      <td>POINT (-74.02778 40.63146)</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Caesar's Bay Shopping Center</td>
      <td>8973 Bay Parkway,Brooklyn, NY 11214</td>
      <td>1148427.411</td>
      <td>0.93</td>
      <td>9d8c13b5b4a93591f427d3ce0b5b4ead</td>
      <td>POINT (-95.45238 29.83378)</td>
    </tr>
  </tbody>
</table>
</div>


```python
geo_name_cdf.gc_status_rel.unique()
```

```
array([0.95, 0.93, 0.96, 0.83, 0.78, 0.9 ])
```

```python
geo_cdf.head()
```

<div>
<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>address</th>
      <th>revenue</th>
      <th>gc_status_rel</th>
      <th>carto_geocode_hash</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Franklin Ave &amp; Eastern Pkwy</td>
      <td>341 Eastern Pkwy,Brooklyn, NY 11238</td>
      <td>1321040.772</td>
      <td>0.97</td>
      <td>c834a8e289e5bce280775a9bf1f833f1</td>
      <td>POINT (-73.95901 40.67109)</td>
    </tr>
    <tr>
      <th>2</th>
      <td>607 Brighton Beach Ave</td>
      <td>607 Brighton Beach Avenue,Brooklyn, NY 11235</td>
      <td>1268080.418</td>
      <td>0.99</td>
      <td>7d39a3fff93efd9034da88aa9ad2da79</td>
      <td>POINT (-73.96122 40.57796)</td>
    </tr>
    <tr>
      <th>3</th>
      <td>65th St &amp; 18th Ave</td>
      <td>6423 18th Avenue,Brooklyn, NY 11204</td>
      <td>1248133.699</td>
      <td>0.98</td>
      <td>1a2312049ddea753ba42bf77f5ccf718</td>
      <td>POINT (-73.98976 40.61912)</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Bay Ridge Pkwy &amp; 3rd Ave</td>
      <td>7419 3rd Avenue,Brooklyn, NY 11209</td>
      <td>1185702.676</td>
      <td>0.98</td>
      <td>827ab4dcc2d49d5fd830749597976d4a</td>
      <td>POINT (-74.02744 40.63152)</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Caesar's Bay Shopping Center</td>
      <td>8973 Bay Parkway,Brooklyn, NY 11214</td>
      <td>1148427.411</td>
      <td>0.98</td>
      <td>119a38c7b51195cd4153fc81605a8495</td>
      <td>POINT (-74.00098 40.59321)</td>
    </tr>
  </tbody>
</table>
</div>

```python
geo_cdf.gc_status_rel.unique()
```

```
array([0.97, 0.99, 0.98])
```

#### Visualize the results

Finally, we can visualize through CARTOframes helpers the geocoding results by precision.

```python
from cartoframes.viz.helpers import color_bins_layer
from cartoframes.viz import Popup

color_bins_layer(
    geo_cdf,
    'gc_status_rel',
    method='equal',
    bins=geo_cdf.gc_status_rel.unique().size,
    title='Geocoding Precision',
    popup=Popup({
        'hover': [{
                'title': 'Address',
                'value': '$address'
            }, {
                'title': 'Precision',
                'value': '$gc_status_rel'
            }]
    })
)
```

<div class="example-map">
    <iframe
        id="guides_location_data_services__geocoding"
        src="https://cartoframes.carto.com/kuviz/c3ae7b8c-3d8c-44fe-87f2-144a83ce9c7d"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

### Isolines

There are two **Isolines** functions: **isochrones** and **isodistances**. In this guide we're using the **isochrones** to know the walking area by time for each Starbucks store and the **isodistances** to discover the walking area by distance.

By definition, isolines are concentric polygons that display equally calculated levels over a given surface area, and they are calculated as the intersection areas from the origin point, measured by:

* **Time** in the case of **isochrones**
* **Distance** in the case of **isodistances**

### Isolines: Isochrones

We're going to use these values to set the ranges: 5, 15 and 30 min. These ranges are in `seconds`, so they will be **300**, **900**, and **1800** respectively.

```python
from cartoframes.data.services import Isolines

iso_service = Isolines()

_, isochrones_dry_metadata = iso_service.isochrones(geo_cdf, [300, 900, 1800], mode='walk', dry_run=True)
```

Remember to always **check the quota** using `dry_run` parameter and `available_quota` method before running the service!

```python
print('available {0}, required {1}'.format(
    iso_service.available_quota(),
    isochrones_dry_metadata.get('required_quota'))
)
```

```
available 1437, required 30
```

```python
isochrones_cdf, isochrones_metadata = iso_service.isochrones(geo_cdf, [300, 900, 1800], mode='walk')
```

```python
isochrones_cdf.head()
```

<div>
<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>source_id</th>
      <th>data_range</th>
      <th>lower_data_range</th>
      <th>geometry</th>
      <th>range_label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>300</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-73.95911 40.67183, -73.95917 ...</td>
      <td>5 min.</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>900</td>
      <td>300</td>
      <td>POLYGON ((-73.95934 40.68011, -73.95839 40.680...</td>
      <td>15 min.</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>1800</td>
      <td>900</td>
      <td>POLYGON ((-73.95949 40.69066, -73.95753 40.692...</td>
      <td>30 min.</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>300</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-73.96177 40.58098, -73.96201 ...</td>
      <td>5 min.</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>900</td>
      <td>300</td>
      <td>POLYGON ((-73.96229 40.57502, -73.96232 40.575...</td>
      <td>15 min.</td>
    </tr>
  </tbody>
</table>
</div>

#### The isolines helper

The most straight forward way of visualizing the the resulting geometries is by using the `isolines_layer` helper. It will use the `range_label` column added automatically by the service to classify each polygon by category.


```python
from cartoframes.viz.helpers import isolines_layer

isolines_layer(isochrones_cdf)
```

<div class="example-map">
    <iframe
        id="guides_location_data_services__isochrones_1"
        src="https://cartoframes.carto.com/kuviz/dbab6a03-1e0f-4fc2-89fd-cdcdd76691ee"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

### Isolines: Isodistances

The isoline services accepts several options to manually change the `resolution` or the `quality` of the polygons. There's more information about these settings in the [Isolines Reference](/developers/cartoframes/reference/#heading-Isolines)


```python
isodistances_cdf, isodistances_dry_metadata = iso_service.isodistances(
    geo_cdf,
    [900, 1800, 3600],
    mode='walk',
    resolution=16.0,
    quality=1,
    dry_run=True
)
```

```python
print('available {0}, required {1}'.format(
    iso_service.available_quota(),
    isodistances_dry_metadata.get('required_quota'))
)
```

```
  available 1407, required 30
```


```python
isodistances_cdf, isodistances_metadata = iso_service.isodistances(
    geo_cdf,
    [900, 1800, 3600],
    mode='walk',
    mode_traffic='enabled',
    resolution=16.0,
    quality=2
)
```


```python
isodistances_cdf.head()
```

<div>
<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>source_id</th>
      <th>data_range</th>
      <th>lower_data_range</th>
      <th>geometry</th>
      <th>range_label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-73.95911 40.67183, -73.95917 ...</td>
      <td>15 min.</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>1800</td>
      <td>900</td>
      <td>POLYGON ((-73.95953 40.67636, -73.95895 40.675...</td>
      <td>30 min.</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>3600</td>
      <td>1800</td>
      <td>POLYGON ((-73.95968 40.68235, -73.95882 40.682...</td>
      <td>60 min.</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>900</td>
      <td>0</td>
      <td>MULTIPOLYGON (((-73.96163 40.58063, -73.96221 ...</td>
      <td>15 min.</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>1800</td>
      <td>900</td>
      <td>POLYGON ((-73.96180 40.57505, -73.96193 40.575...</td>
      <td>30 min.</td>
    </tr>
  </tbody>
</table>
</div>

```python
from cartoframes.viz.helpers import isolines_layer

isolines_layer(isodistances_cdf)
```

<div class="example-map">
    <iframe
        id="guides_location_data_services__isodistances_1"
        src="https://cartoframes.carto.com/kuviz/acc87a0e-1e06-40c8-b05f-b45b6e26bef1"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

### All together


```python
from cartoframes.viz import Map
from cartoframes.viz.helpers import size_continuous_layer

Map([
    isolines_layer(
        isochrones_cdf,
        title='Walking Time'
    ),
    size_continuous_layer(
        geo_cdf,
        'revenue',
        title='Revenue $',
        color='white',
        opacity='0.2',
        stroke_color='blue',
        size=[20, 80],
        popup=Popup({
            'hover': [{
                    'title': 'Address',
                    'value': '$address'
                }, {
                    'title': 'Precision',
                    'value': '$gc_status_rel'
                }, {
                    'title': 'Revenue',
                    'value': '$revenue'
                }]
        })
    )
])
```

<div class="example-map">
    <iframe
        id="guides_location_data_services__all_togehter_1"
        src="https://cartoframes.carto.com/kuviz/f1159959-80a9-4e0e-9a49-ff11b118f01d"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

We observe the store at 228 Duffield st, Brooklyn, NY 11201 is really close to another store with higher revenue, which means we could even think about closing that one in favor to another one with a better location.

We could try to calculate where to place a new possible store between other stores that don't have as much revenue as others and that are placed separately.

Now, let's calculate the **centroid** of three different stores that we've identified previously and use it as a possible location for a new spot:

```python
from shapely import geometry
import geopandas as gpd

# Create a polygon using three points from the geo_cdf
polygon = geometry.Polygon([[p.x, p.y] for p in geo_cdf.iloc[[1, 6, 9]])

new_store_gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(polygon.centroid))
```

```python
from cartoframes.viz import Layer

isochrones_new_cdf, isochrones_new_metadata = iso_service.isochrones(new_store_df, [300, 900, 1800], mode='walk')
```

```python
Map([
    isolines_layer(
        isochrones_cdf,
        title='Walking Time - Current',
        opacity='0.2'
    ),
    isolines_layer(
        isochrones_new_cdf,
        title='Walking Time - New',
    ),
    size_continuous_layer(
        geo_cdf,
        'revenue',
        title='Revenue $',
        color='white',
        opacity='0.2',
        stroke_color='blue',
        size=[20, 80],
        popup=Popup({
            'hover': [{
                    'title': 'Address',
                    'value': '$address'
                }, {
                    'title': 'Precision',
                    'value': '$gc_status_rel'
                }, {
                    'title': 'Revenue',
                    'value': '$revenue'
                }]
        })
    )
])
```

<div class="example-map">
    <iframe
        id="guides_location_data_services__analysis"
        src="https://cartoframes.carto.com/kuviz/23a4c793-3ac9-4be3-84a2-70a0b10086d0"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>

### Conclusion

In this example we've explained how to use the Location Data Services to perform trade areas analysis easily using CARTOframes built-in functionality without leaving the notebook.

As a result, we've calculated a possible new location for our store, and we can check how the isoline areas of our interest can influence in our decission.

Take into account that finding optimal spots for new stores is not an easy task and requires more analysis, but this is a great first step!
