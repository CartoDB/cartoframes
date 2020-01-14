## Location Data Services

### Introduction

CARTOframes provides the functionality to use the [CARTO Data Services API](https://carto.com/developers/data-services-api/). This API consists of a set of location-based functions that can be applied to your data to perform geospatial analyses without leaving the context of your notebook.

For instance, you can **geocode** a pandas DataFrame with addresses on the fly, and then perform a trade areas analysis by computing **isodistances** or **isochrones** programmatically.

Given a set of ten simulated Starbucks store addresses, this guide walks through the use case of finding good location candidates to open an additional store.

> Based on your account plan, some of these location data services are subject to different [quota limitations](https://carto.com/developers/data-services-api/support/quota-information/)

### Data

This guide uses the same dataset of simulated Starbucks locations that has been used in the other guides and can be downloaded [here](http://libs.cartocdn.com/cartoframes/files/starbucks_brooklyn.csv).

### Authentication

Using Location Data Services requires CARTO authentication. For more information about how to authenticate, please read the [Authentication guide](/developers/cartoframes/guides/Authentication/).

```python
from cartoframes.auth import set_default_credentials

set_default_credentials('creds.json')
```

### Geocoding

To get started, let's read in and explore the Starbucks location data we have. With the Starbucks store data in a DataFrame, we can see that there are two columns that can be used in the **geocoding** service: `name` and `address`. There's also a third column that reflects the annual revenue of the store.

```python
import pandas

df = pandas.read_csv('http://libs.cartocdn.com/cartoframes/files/starbucks_brooklyn.csv')
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

Each time you run Location Data Services, you consume quota. For this reason, we provide the ability to check in advance the **amount of credits** an operation will consume by using the `dry_run` parameter when running the service function.

It is also possible to check the available quota by running the `available_quota` function.

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
geo_gdf, geo_metadata = geo_service.geocode(
    df,
    street='address',
    city={'value': 'New York'},
    country={'value': 'USA'}
)
```

If the input data file should ever change, cached results will only be applied to unmodified
records, and new geocoding will be performed only on _new or changed records_.

In order to use cached results, we have to save the results to a CARTO table using the `table_name` and `cached=True` parameters.

```python
geo_gdf_cached, geo_metadata_cached = geo_service.geocode(
    df,
    street='address',
    city={'value': 'New York'},
    country={'value': 'USA'},
    table_name='starbucks_cache',
    cached=True
)
```

Let's compare `geo_dry_metadata` and `geo_metadata` to see the differences between the information returned with and without the `dry_run` option. As we can see, this information reflects that all the locations have been geocoded successfully and that it has consumed 10 credits of quota.

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

The resulting data is a `GeoDataFrame` that contains three new columns:

* `geometry`: The resulting geometry
* `gc_status_rel`: The percentage of accuracy of each location
* `carto_geocode_hash`: Geocode information

```python
geo_gdf.head()
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

In addition, to prevent geocoding records that have been **previously geocoded**, and thus spend quota **unnecessarily**, you should always preserve the ``the_geom`` and ``carto_geocode_hash`` columns generated by the geocoding process.

This will happen **automatically** in these cases:

1. Your input is a **table** from CARTO processed in place (without a ``table_name`` parameter)
2. If you save your results to a CARTO table using the ``table_name`` parameter, and only use the resulting table for any further geocoding.

If you try to geocode this DataFrame now, that contains both ``the_geom`` and the ``carto_geocode_hash``, you will see that the required quota is 0 because it has already been geocoded.

```python
_, repeat_geo_metadata = geo_service.geocode(
    geo_gdf,
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

The `address` column is more complete than the `name` column, and therefore, the resulting coordinates calculated by the service will be more accurate. If we check this, the accuracy values using the `name` column (`0.95, 0.93, 0.96, 0.83, 0.78, 0.9`) are lower than the ones we get by using the `address` column for geocoding (`0.97, 0.99, 0.98`).

```python
geo_name_gdf, geo_name_metadata = geo_service.geocode(
    df,
    street='name',
    city={'value': 'New York'},
    country={'value': 'USA'}
)
```

```python
geo_name_gdf.head()
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
geo_name_gdf.gc_status_rel.unique()
```

```
array([0.95, 0.93, 0.96, 0.83, 0.78, 0.9 ])
```

```python
geo_gdf.head()
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
geo_gdf.gc_status_rel.unique()
```

```
array([0.97, 0.99, 0.98])
```

#### Visualize the results

Finally, we can visualize the precision of the geocoded results using a CARTOframes [visualization layer](/developers/cartoframes/examples/#example-color-bins-layer).

```python
from cartoframes.viz import Map, Layer, color_bins_style, popup_element

Map(
  Layer(
    geo_gdf,
    color_bins_style(
      'gc_status_rel',
      method='equal',
      bins=geo_gdf.gc_status_rel.unique().size
    ),
    popup_hover=[
      popup_element('address', title='Address'),
      popup_element('gc_status_rel', title='Precision'),
    ],
    title='Geocoding Precision'
  )
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

There are two **Isoline** functions: **isochrones** and **isodistances**. In this guide we will use the **isochrones** function to calculate walking areas _by time_ for each Starbucks store and the **isodistances** function to calculate the walking area _by distance_.

By definition, isolines are concentric polygons that display equally calculated levels over a given surface area, and they are calculated as the intersection areas from the origin point, measured by:

* **Time** in the case of **isochrones**
* **Distance** in the case of **isodistances**

### Isochrones

For isochones, let's calculate the time ranges of: 5, 15 and 30 min. These ranges are input in `seconds`, so they will be **300**, **900**, and **1800** respectively.

```python
from cartoframes.data.services import Isolines

iso_service = Isolines()

_, isochrones_dry_metadata = iso_service.isochrones(geo_gdf, [300, 900, 1800], mode='walk', dry_run=True)
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
isochrones_gdf, isochrones_metadata = iso_service.isochrones(geo_gdf, [300, 900, 1800], mode='walk')
```

```python
isochrones_gdf.head()
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

The most straightforward way of visualizing the resulting geometries is to use the `isolines_style` visualization layer. This visualization layer uses the `range_label` column that is automatically added by the service to classify each polygon by category.

```python
from cartoframes.viz import Layer, isolines_style

Layer(isochrones_gdf, isolines_style())
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

### Isodistances

The isoline services accepts several options to manually change the `resolution` or the `quality` of the polygons. There's more information about these settings in the [Isolines Reference](/developers/cartoframes/reference/#heading-Isolines)


```python
isodistances_gdf, isodistances_dry_metadata = iso_service.isodistances(
    geo_gdf,
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
isodistances_gdf, isodistances_metadata = iso_service.isodistances(
    geo_gdf,
    [900, 1800, 3600],
    mode='walk',
    mode_traffic='enabled',
    resolution=16.0,
    quality=2
)
```

```python
isodistances_gdf.head()
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
from cartoframes.viz import Layer, isolines_style

Layer(isochrones_gdf, isolines_style())
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

Let's visualize the data in one map to see what insights we can find.

```python
from cartoframes.viz import Map, Layer, isolines_style, size_continuous_style, popup_element

Map([
    Layer(
        isochrones_gdf,
        isolines_style(),
        title='Walking Time'
    ),
    Layer(
        geo_gdf,
        size_continuous_style(
            'revenue',
            color='white',
            opacity='0.2',
            stroke_color='blue',
            size_range=[20, 80],
        ),
        popup_hover=[
            popup_element('address', 'Address'),
            popup_element('gc_status_rel', 'Precision'),
            popup_element('revenue', 'Revenue')
        ],
        title='Revenue $',
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

Looking at the map above, we can see the store at 228 Duffield St, Brooklyn, NY 11201 is really close to another store with higher revenue, which means we could even think about closing that one in favor of another one with a better location.

We could try to calculate where to place a new store between other stores that don't have as much revenue as others and that are placed separately.

Now, let's calculate the **centroid** of three different stores that we've identified previously and use it as a possible location for a new spot:

```python
from shapely import geometry

new_store_location = [
    geo_gdf.iloc[6].the_geom,
    geo_gdf.iloc[9].the_geom,
    geo_gdf.iloc[1].the_geom
]

# Create a polygon using three points from the geo_gdf
polygon = geometry.Polygon([[p.x, p.y] for p in new_store_location])
```

```python
from geopandas import GeoDataFrame, points_from_xy

new_store_gdf = GeoDataFrame({
    'name': ['New Store'],
    'geometry': points_from_xy([polygon.centroid.x], [polygon.centroid.y])
})

isochrones_new_gdf, isochrones_new_metadata = iso_service.isochrones(new_store_gdf, [300, 900, 1800], mode='walk')
```

```python
from cartoframes.viz import Map, Layer, isolines_style, size_continuous_style

Map([
    Layer(
        isochrones_gdf,
        isolines_style(opacity='0.2'),
        title='Walking Time - Current'
    ),
    Layer(
        isochrones_new_gdf,
        isolines_style(),
        title='Walking Time - New'
    ),
    Layer(
        geo_gdf,
        size_continuous_style(
            'revenue',
            color='white',
            opacity='0.2',
            stroke_color='blue',
            size_range=[20, 80]
        ),
        popup_hover=[
            popup_element('address', 'Address'),
            popup_element('gc_status_rel', 'Precision'),
            popup_element('revenue', 'Revenue')
        ],
        title='Revenue $',
    ),
    Layer(new_store_gdf)
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

In this example you've seen how to use Location Data Services to perform a trade area analysis using CARTOframes built-in functionality without leaving the notebook.

Using the results, we've calculated a possible new location for a store, and used the isoline areas to help in the decision making process.

Take into account that finding optimal spots for new stores is not an easy task and requires more analysis, but this is a great first step!
