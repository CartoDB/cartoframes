## Spatial Analysis

### About this Guide

This guide walks you through methods to implement spatial analysis using CARTOframes. CARTOframes provides the `CartoContext.query` method for performing analysis and returning the results as a pandas dataframe, and the `QueryLayer` class for visualizing analysis as a map layer. Both methods run the quries against a [PostgreSQL](https://www.postgresql.org/) database with [PostGIS](http://postgis.net/). CARTO also provides more advanced spatial analysis through the [`crankshaft` extension](https://github.com/cartodb/crankshaft/).

In this guide, we will analyze McDonald's locations in US Census tracts using spatial analysis functionality in CARTO.

### Getting Started

To get started, create a `CartoContext`:

```python
from cartoframes import CartoContext, QueryLayer, BaseMap
cc = CartoContext(base_url='<your_base_url>',
                  api_key='<your_api_key>')
```

To load New York City Census Tract Boundaries, you can either download it from [US Census Bureau](https://www.census.gov/cgi-bin/geo/shapefiles/index.php) or use CARTOframes' `examples.read_nyc_census_tracts` function to request it. This dataset was originally retrieved from CARTO's Data Observatory (DO) but stored in the examples account to avoid consuming DO quota. Check out the [next guide](../Data-Observatory/) for more DO interactions within CARTOframes.

```python
from cartoframes.examples import read_nyc_census_tracts
nyc_ct = read_nyc_census_tracts()
```

For New York City McDonald's Locations data, we'll load it from the CARTOframes examples account as well:

```python
from cartoframes.examples import read_mcdonalds_nyc
mcd = read_mcdonalds_nyc()
```

Then write both datasets to your CARTO account.

```python
cc.write(nyc_ct, 'nyc_census_tracts')
cc.write(mcd, 'nyc_mcdonalds')
```

### Running a SQL query

Use the `CartoContext.query` method to run a SQL query for the datasets in your CARTO account. PostGIS includes multiple spatial analysis functions like `ST_Intersects` and `ST_Buffer`. CARTO's [spatial analysis library crankshaft](https://github.com/CartoDB/crankshaft/tree/develop/doc) provides additional advanced spatial analysis functions like spatial k-means (`cdb_kmeans`) and Moran's I Local (`cdb_moransilocal`).

#### Example 1

Find the number of McDonald's in each census tract in New York City.

```python
df = cc.query('''
    SELECT
      tracts.geom_refs AS FIPS_code,
      tracts.the_geom as the_geom,
      COUNT(mcd.*) AS num_mcdonalds
    FROM nyc_census_tracts As tracts, nyc_mcdonalds As mcd
    WHERE ST_Intersects(tracts.the_geom, mcd.the_geom)
    GROUP BY tracts.geom_refs
    ORDER BY num_mcdonalds DESC
''')

# Show first five entries of results
# Including FIPS code (unique digital identifier for census tracts) and the number of McDonald's
# Sorted by the number of McDonald's in descending order
df.head()
```

|      |  fips_code  | num_mcdonalds |
| :--: | :---------: | :-----------: |
|  0   | 36061010100 |       4       |
|  1   | 36061007100 |       2       |
|  2   | 36061011300 |       2       |
|  3   | 36061010900 |       2       |
|  4   | 36061001502 |       2       |

#### Example 2

Build 100 meter buffer area for each McDonald's by updating the geometry.

```python
# Be Careful - this will change the original table in your account
cc.query("""
    UPDATE nyc_mcdonalds
    SET the_geom = ST_Buffer(the_geom::geography, 100)::geometry
""")

df = cc.query(
    '''
    SELECT name, id, address, city, zip, the_geom
    FROM nyc_mcdonalds
    ''',
    decode_geom=True
)

# or create a new table and save it as 'nyc_mcdonalds_buffer_100m'.
df = cc.query(
    '''
        SELECT name, id, address, city, zip,
               ST_Buffer(the_geom::geography, 100)::geometry AS the_geom
        FROM nyc_mcdonalds
    ''',
    table_name='nyc_mcdonalds_buffer_100m')

# Show the first entry.
# 'geomtery' is Polygon type now.
df = cc.read('nyc_mcdonalds_buffer_100m', decode_geom=True)
df.iloc[0, :]
```

| address  |                                 1101 E Tremont Ave |
| city     |                                              Bronx |
| id       |                                                233 |
| name     |                                         McDonald's |
| the_geom |  0106000020E61000000100000001030000000100000021... |
| zip      |                                              10460 |
| geometry |  (POLYGON ((-73.87570453921256 40.8403982178504... |

To show the results of this query on a map, we can do the following:

```python
from cartoframes import Layer, QueryLayer
cc.map(layers=[
    Layer('nyc_mcdonalds', color='red', size=3),
    Layer('nyc_mcdonalds_buffer_100m', color='#aaa')
])
```

![](../../img/guides/03-spatial-analysis-1.png)

### Mapping a SQL query

Use table names or `QueryLayer` inside the `CartoContext.map` method to demonstrate analysis results.


#### Example 3

Apply k-means (k=5) spatial clustering for all McDonald's in NYC, and visualize different clusters by color. Note: for more complicated queries, it is best to create a temporary table from the query and then visualize it.

```python
tmp = cc.query('''
       SELECT
         row_number() OVER () AS cartodb_id,
         c.cluster_no,
         c.the_geom,
         ST_Transform(c.the_geom, 3857) AS the_geom_webmercator
       FROM
         ((SELECT *
           FROM cdb_crankshaft.cdb_kmeans(
               'SELECT the_geom, cartodb_id, longitude, latitude FROM nyc_mcdonalds', 5)
          ) AS a
           JOIN
         nyc_mcdonalds AS b
         ON a.cartodb_id = b.cartodb_id
         ) AS c
              ''',
    table_name='mcd_clusters')

cc.map(Layer('mcd_clusters',
             color={'column': 'cluster_no',
                    'scheme': styling.prism(5)}),
      interactive = True)             
```
![kmeans](../../img/guides/03-KMeans.png)

Users also can drop temporary tables using `delete` function after map plotting. Note that static images will be preserved in a Jupyter notebook, but interactive maps will cease to work if they still reference a deleted table.

```python
cc.delete('mcd_clusters')
```

#### Example 4

Apply Moran's I to detect hot spots and cold spots of median household income at census tract level in Manhattan.

```python
# Augment median_household_income data from DO
median_income = [{'numer_id': 'us.census.acs.B19013001',
                  'geom_id': 'us.census.tiger.census_tract',
                  'numer_timespan': '2011 - 2015'}]

# look up measures using GEOID in the `geom_refs` column
df = cc.data('nyc_census_tracts', median_income, how='geom_refs')

# Filter census tracts from Manhattan.
# Keep those whose 'median_income_2011_2015' values aren't 'NaN'.
df['is_manhattan'] = df.apply(lambda x: x.geom_refs.startswith("36061"), axis=1)
manhattan = df[df['is_manhattan'] == True]
manhattan.dropna(subset=['median_income_2011_2015'], inplace=True)

# Save the dataframe to your CARTO account
cc.write(manhattan, 'manhattan_median_income', overwrite=True)

tmp = cc.query('''
    SELECT
      m.*,
      t.the_geom,
      t.the_geom_webmercator,
      t.cartodb_id
    FROM
      cdb_crankshaft.cdb_moransilocal(
        'SELECT * FROM manhattan_median_income',
        'median_income_2011_2015') AS m
    JOIN manhattan_median_income AS t
    ON t.cartodb_id = m.rowid
''')
cc.write(tmp, 'tmp', overwrite=True)

# The map shows Hot Spots in 'red' and Cold Spots in 'blue'
cc.map(layers=[
    BaseMap('dark'),
    QueryLayer("""
            SELECT * FROM tmp
            WHERE significance < 0.05 AND quads IN ('LL', 'HH')
            """,
            color={'column': 'quads',
                   'scheme': styling.custom(colors=['blue', 'red'],
                                            bin_method='category')})],
    interactive=False)
```

![Moran's I result](../../img/guides/03-Moran_i.png)
