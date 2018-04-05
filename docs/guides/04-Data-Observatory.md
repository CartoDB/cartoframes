## Data Observatory

Access data from CARTO's Data Observatory (DO). Augment your tables with measures and
get boundaries available in the DO.

### Querying Metadata

The full metadata for a DO variable uniquely defines a measure based on the time or timespan vintage,
geographic resolution, and normalization method, if any. Read more about the metadata response in [Data Observatory documentation](https://carto.com/docs/carto-engine/data/measures-functions/#obs_getmetaextent-geometry-metadata-json-max_timespan_rank-max_score_rank-target_geoms).

Search metadata for all United States measures from the 2011 - 2015 American Community Survey
that mention median income, using regex. The results are returned as a Pandas DataFrame.

```python
median_income = cc.data_discovery('United States',
                                  regex='.*median income.*',
                                  time='2011 - 2015')
```

Search metadata for all measures from the 2011 - 2015 American Community Survey (ACS) 5-year Estimates
that mentions education by using a keyword search and matching with the geographic extent of your table.

```python
median_income = cc.data_discovery('my_table',
                                  keyword='education',
                                  timespan='2011 - 2015')
```

### Augmenting your data

Once you have identified the correct metadata for the DO variables you want, you can augment
an existing CARTO dataset and return it as a Pandas DataFrame. There are two methods
for passing in metadata to augment.

1. Pass the metadata DataFrame created from `cc.data_discovery` into `cc.data`

```python
median_income = cc.data_discovery('my_table',
                                  keyword='education',
                                  timespan='2011 - 2015')
df = cc.data('my_table',
             median_income)
```

2. Or, you can pass in cherry-picked measures from the [Data Observatory catalog](https://cartodb.github.io/bigmetadata/index.html) as a list of dictionaries.
The rest of the metadata will be filled in,
but it’s important to specify the geographic level.

```python
total_population = [{'numer_id': 'us.census.acs.B01003001',
                  'geom_id': 'us.census.tiger.block_group',
                  'numer_timespan': '2011 - 2015'}]
df = cc.data('my_table', total_population)
```

Additionally, you can persist the results as a new CARTO table by passing a new
table name.

```python
df = cc.data('my_table', total_population, persist_as='my_table_population')
```

### Accessing and finding boundaries

Find all the boundaries available in the world, or in a region or country.

```python
all_available_boundaries = cc.data_boundaries()
```

If you pass a boundary id, you will be returned with a table of the geom_refs
and the_geom in WKT format. This query finds and returns all the boundaries for
Australia Postal Areas.

```python
au_postal_areas = cc.data_boundaries(boundary='au.geo.POA')
```

We can also ask decode the WKB geometries into Shapely objects.

```python
au_postal_areas = cc.data_boundaries(boundary='au.geo.POA', decode_geom=True)
```

### Getting raw measures and boundaries

Let's start without any data and find boundaries and augment them with data.

In this example, we'll get the population density of all the US counties as of the 2015 ACS 1-year Estimates

```python
# find all US counties
us_counties = cc.data_boundaries(boundary='us.census.tiger.county', timespan='2015')

# write geometries to a CARTO table
cc.write(us_counties, 'us_counties')

# define metadata structure
total_pop = [{'numer_id':'us.census.acs.B01003001',
              'geom_id':'us.census.tiger.county',
              'timespan':'2015 - 2015'}]

# augment dataset and persist as a new dataset
df = cc.data('us_counties', total_pop, persist_as='us_counties_population')

#  create a choropleth map based on total population per a square kilometer.
cc.map(layers=Layer('us_counties_population', color='total_pop_per_sq_km_2015_2015'))
```
