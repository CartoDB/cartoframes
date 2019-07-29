## Spatial Analysis

### About this Guide

CARTOframes provides the `Dataset(your_query)` method for performing analysis and returning the results as a pandas dataframe, and the `Layer` class for visualizing analysis as a map layer. Both methods run the quries against a **PostgreSQL** database with **PostGIS**. CARTO also provides more advanced spatial analysis through the crankshaft extension.

In this guide, we will analyze McDonald’s locations in US Census tracts using spatial analysis functionality in CARTO.

You can download directly the dataset from their sources:

- [NYC Census Tracts Data](https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2018&layergroup=Census+Tracts)
- [NYC McDonald's](https://data.cityofnewyork.us/Health/McDonald-s/kyws-ad2t)

Or follow the following steps to download them directly from the CARTOframes account.

### Getting Started

#### Create the contexts:

```py
from cartoframes.auth import Credentials
from cartoframes.viz import Map, Layer, Legend, Source
from cartoframes.data import Dataset

## Add here your CARTO credentials:
credentials = Credentials(base_url='https://your_user_name.carto.com', api_key='your_api_key')
cf_credentials = Credentials(base_url='https://cartoframes.carto.com', api_key='default_public')
```

#### Get the data

And upload it to your account:

McDonald's:

```py
mcdonalds_nyc_data = Dataset('mcdonalds_nyc', credentials=cf_credentials)
mcdonalds_nyc_data_df = mcdonalds_nyc_data.download()

mcdonalds_nyc = Dataset(mcdonalds_nyc_data_df)
mcdonalds_nyc.upload(table_name='mcdonalds_nyc', if_exists='replace', credentials=credentials)
```

NYC Census Tracts:

```py
nyc_census_tracts_data = Dataset('nyc_census_tracts', credentials=cf_credentials)
nyc_census_tracts_data_df = nyc_census_tracts_data.download()

nyc_census_tracts = Dataset(nyc_census_tracts_data_df)
nyc_census_tracts.upload(table_name='nyc_census_tracts', if_exists='replace', credentials=credentials)
```

### Example 1

Find the number of McDonald’s in each census tract in New York City.

```py
mcdonalds_per_census_tracts = Dataset('''
    SELECT
      tracts.geom_refs AS FIPS_code,
      tracts.the_geom as the_geom,
      COUNT(mcd.*) AS num_mcdonalds
    FROM nyc_census_tracts As tracts, mcdonalds_nyc As mcd
    WHERE ST_Intersects(tracts.the_geom, mcd.the_geom)
    GROUP BY tracts.geom_refs, tracts.the_geom
    ORDER BY num_mcdonalds DESC
''', credentials=credentials)
```

```py
# Show first five entries of results
# Including FIPS code (unique digital identifier for census tracts) and the number of McDonald's
# Sorted by the number of McDonald's in descending order
mcdonalds_per_census_tracts = mcdonalds_per_census_tracts.download()
mcdonalds_per_census_tracts.head()
```

|   | fips_code | num_mcdonalds |
|:-:|:-:|:-:|
| 0 | 36061010100 | 4 |
| 1 | 36061007100 | 2 |
| 2 | 36047025500 | 2 |
| 3 | 36061011300 | 2 |
| 4 | 36061010900 | 2 |

### Example 2

Build 100 meter buffer area for each McDonald’s by updating the geometry.

#### Create a new table and save it as `nyc_mcdonalds_buffer_100m`.

```py
nyc_mcdonalds_buffer_100m = Dataset(
    '''
    SELECT name, id, address, city, zip,
        ST_Buffer(the_geom::geography, 100)::geometry AS the_geom
    FROM mcdonalds_nyc
    ''',
    credentials=credentials)

nyc_mcdonalds_buffer_100m.upload(table_name='nyc_mcdonalds_buffer_100m', if_exists='replace', credentials=credentials)
nyc_mcdonalds_buffer_100m_df = nyc_mcdonalds_buffer_100m.download()
nyc_mcdonalds_buffer_100m_df.iloc[0, :]
```

#### Visualize the results:

```py
from cartoframes.viz import Map, Layer

Map([
    Layer('nyc_mcdonalds_buffer_100m', 'color: lightgray width: 20', credentials=credentials),
    Layer('mcdonalds_nyc', 'color: red width: 3', credentials=credentials),
  ],
  viewport={'zoom': 13.00, 'lat': 40.74, 'lng': -73.98}
)
```

[Live Visualization](https://cartovl.carto.com/kuviz/a6a586c3-682c-4591-a8cd-f4d9d4cc10bd)
![NYC McDonald's 100 Metter area](../../img/guides/spatial-analysis/example-2.png)

### Example 3

1. Apply k-means (k=5) spatial clustering for all McDonald’s in NYC, and visualize different clusters by color.

> Note: for more complicated queries, it is best to create a temporary table from the query and then visualize it.

```py
k_means_dataset = Dataset('''
       SELECT
         row_number() OVER () AS cartodb_id,
         con.cluster_no,
         con.the_geom,
         ST_Transform(c.the_geom, 3857) AS the_geom_webmercator
       FROM
         ((SELECT *
           FROM cdb_crankshaft.cdb_kmeans(
               'SELECT the_geom, cartodb_id, longitude, latitude FROM mcdonalds_nyc', 5)
          ) AS a
           JOIN
         mcdonalds_nyc AS b
         ON a.cartodb_id = b.cartodb_id
         ) AS c
        ''',
        credentials=credentials)

k_means_dataset.upload(table_name='mcdonalds_clusters', if_exists='replace', credentials=credentials)
```

#### Visualize the results:

```py
from cartoframes.viz import Map, Layer

Map(Layer('mcdonalds_clusters', 'color: ramp($cluster_no, Prism)', credentials=credentials))
```

[Live Visualization](https://cartovl.carto.com/kuviz/8c5b6b66-ab5e-41d3-b3e5-c2d08d6831d4)
![NYC McDonald's Cluster](../../img/guides/spatial-analysis/example-3.png)
