## Spatial Analysis

CARTOframes provides `query` and `QueryLayer` functions to run spatial analysis based on PostgreSQL and PostGIS. Users can receive query results as `pandas.DataFrame` format as well as demonstrate them in maps.

### Getting Started

TODO: get census tracts from DO for nyc

### Running a SQL query
Use `query` function to run SQL query for the datasets in your CARTO account. PostgreSQL and PostGIS include multiple spatial analysis functions like `ST_Intersects`, `ST_buffer` and so on.

TODO: link to docs: https://github.com/CartoDB/crankshaft/tree/develop/doc

```python
# Find the number of McDonald's in each census tract in New York City
df = cc.query("""
    SELECT tracts.boroct2010, COUNT(mcd.*) AS num_mcdonalds
    FROM nyct As tracts, nyc_mcdonalds As mcd
    WHERE ST_Intersects(a.the_geom, mcd.the_geom)
    GROUP BY a.boroct2010
    ORDER BY num_mcdonalds DESC
""")

# show first five entries of results
df.head()
```

TODO: description of what's going on in the query below

```python
# Build 100 meters buffer area for each McDonald's.
cc.query("""
    UPDATE nyc_mcdonalds
    SET the_geom = ST_Buffer(the_geom, 100)
""")
```

### Maping an SQL query
Use `QueryLayer` inside `map` function to demonstrate analysis results. Besides PostgreSQL and PostGIS built-in functions, CARTO also provides multiple advanced spatial analysis functions like `cdb_kmeans`, `cdb_moransilocal` and so on.

```python
# Apply KMeans (k=5) method
# Spatial Clustering for all McDonald's
# Visualize different clusters by different colors
tmp = cc.query("""
    SELECT * FROM (
        SELECT
          row_number() over() AS cartodb_id,
          c.cluster_no,
          c.the_geom,
          ST_Transform(c.the_geom, 3857) AS the_geom_webmercator
        FROM
          ((SELECT * FROM cdb_crankshaft.cdb_kmeans('SELECT * FROM nyc_mcdonalds', 5)) a
            JOIN
          nyc_mcdonalds b
          ON
          a.cartodb_id = b.cartodb_id
          ) c
    )
               """,
              table_name='tmp')
cc.map(Layer("tmp", color={'column': 'cluster_no',
                           'scheme': styling.prism(5)}))
```

TODO? this is possible to drop a table
```python
cc.delete('tmp')
```


```python
# Apply Moran's I Analysis
# Detect Hot Spots & Cold Spots of
# Median Household Income at Census Tract Level
# In Manhattan
median_income = [{'numer_id': 'us.census.acs.B19013001',
                  'geom_id': 'us.census.tiger.census_tract',
                  'numer_timespan': '2011 - 2015'}]
df = cc.data('nyct', median_income)
manhattan = df[df.boroname=='Manhattan']
cc.write(manhattan, 'manhattan_median_income', overwrite=True)

tmp = cc.query("""
            SELECT m.*, t.the_geom, t.the_geom_webmercator, t.cartodb_id
            FROM cdb_crankshaft.cdb_moransilocal('SELECT * FROM manhattan_median_income', 'median_income_2011_2015') as m
            JOIN manhattan_median_income as t
            ON t.cartodb_id = m.rowid
            """)

cc.write(tmp, 'tmp', overwrite=True)

cc.map(layers=[
    BaseMap(),
    QueryLayer("""
            select * from tmp
            where significance < 0.05 and (quads = 'HH' or quads ='LL')
            """,
            color={'column': 'quads',
                   'scheme': styling.vivid(2)})])
```
