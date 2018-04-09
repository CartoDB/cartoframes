## Data Observatory

Access data from CARTO's Data Observatory (DO). Augment your tables with measures and get boundaries available in the DO.

### About this Guide

This guide walks you through most of the common operations for Data Observatory interactions within cartoframes such as measure discovery (via metadata), augmenting datasets with DO measures, and downloading raw or shoreline-clipped boundaries.

**Note**: Data Observatory queries consume quota for all methods below except `CartoContext.data_discovery`.


### Getting Started

To get started, we need to create a `CartoContext` object to interact with CARTO. Do the following, or checkout the QuickStart guide for more information:

```python
from cartoframes import CartoContext
cc = CartoContext(base_url='your base url', api_key='your api key')
```

### Querying Metadata

The full metadata for a DO variable uniquely defines a measure based on the time or timespan vintage, geographic resolution, and normalization method, if any. Read more about the metadata response in [Data Observatory documentation](https://carto.com/docs/carto-engine/data/measures-functions/#obs_getmetaextent-geometry-metadata-json-max_timespan_rank-max_score_rank-target_geoms). Once we have the metadata, we can uniquely download the raw data or augment our existing data by using the `CartoContext.data` method below.

To get started, we'll search metadata for all United States measures from the '2011 - 2015' American Community Survey that mention **median income**. Here we're using the `regex` keyword, which gives us a case insensitive search of measure names and descriptions. The results are returned as a [pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html).

```python
median_income_meta = cc.data_discovery(
    'United States',
    regex='.*median income.*',
    time='2011 - 2015'
)

# view the first five entries of the metadata
median_incom_meta.head()
```

Notice that each row is a unique measure defined by the combination of properies in the columns. If the denominator values are filled in, this means that the numerator is normalized by an appropriate denominator at a specific timespan and geographic level. As you can see from all of the columns, measures can be specified in a large number of ways.

We can also do more traditional keyword searches. Search metadata for all measures from the '2011 - 2015' American Community Survey (ACS) 5-year Estimates that mentions education by using a keyword search and matching with the geographic extent of your table.

```python
education_meta = cc.data_discovery(
    'my_table',
    keyword='education',
    timespan='2011 - 2015'
)

# preview the data
education_meta.head()
```

To more fully inspect an entry, look at the values:

```python
education_meta.iloc[0].values
```

Or even filter futher using pandas' str operations to find education measures that mention 'secondary':

```python
education_meta[education_meta.numer_description.str.contains('secondary')]
```

### Augmenting your data

Once you have identified the correct metadata for the DO variables you want, you can augment
an existing CARTO dataset and return it as a Pandas DataFrame. There are two methods
for passing in metadata to augment.

TODO: add a step where we are getting a specified table so the user can follow along

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
