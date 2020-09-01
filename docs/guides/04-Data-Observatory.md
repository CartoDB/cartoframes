## Data Observatory

### About this Guide

This guide walks you through common operations for Data Observatory (DO) interactions within cartoframes such as measure discovery (via metadata), augmenting datasets with DO measures, and downloading raw or shoreline-clipped boundaries. These methods can be chained in way to give you data from nothing such as getting all US counties, their GEOIDs, and some raw or derived measures.

**Note**: Data Observatory queries consume quota for all methods below except `CartoContext.data_discovery`.

### Getting Started

To get started, we need to create a `CartoContext` object to interact with CARTO and a table with geometries to establish the search area. To get started, we'll load a dataset of New York City census tracts into your account. We get the data from the cartoframes examples account, but the data was originally obtained from the Data Observatory (see the section [Getting boundaries for a specific region](#getting-boundaries-for-a-specific-region) below for the method we used).

```python
from cartoframes import CartoContext, examples
# create CartoContext against your account
# base_url is of the form: https://your_username.carto.com
cc = CartoContext(base_url='<your_base_url>', api_key='<your_api_key>')
# send census tracts to your account
cc.write(examples.load_nyc_census_tracts(), 'nyc_census_tracts')
```

To get a visual preview of the data, create a map of it:

```python
from cartoframes import Layer
cc.map(Layer('nyc_census_tracts'))
```

### Querying Metadata

The full metadata for a DO variable uniquely defines a measure based on the time or timespan vintage, geographic resolution, and normalization method. There are around 42 metadata items for each measure, so the combinations can be nuanced and extensive. Read more about the metadata response in [Data Observatory documentation](https://carto.com/docs/carto-engine/data/measures-functions/#obs_getmetaextent-geometry-metadata-json-max_timespan_rank-max_score_rank-target_geoms). Once we have the metadata, we can uniquely download the raw data or augment our existing data by using the `CartoContext.data` method below.

To get started, we'll search metadata for all United States measures from the '2011 - 2015' American Community Survey (ACS) that mention **median income**. Here we're using the `regex` keyword, which gives us a case insensitive search of measure names and descriptions. The results are returned as a [pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html).

```python
median_income_meta = cc.data_discovery(
    'United States',
    regex='.*median income.*',
    time='2011 - 2015'
)

# view the first five entries of the metadata
median_income_meta.head()
```

Notice that each row is a unique measure defined by the combination of properties in the columns. If the denominator values are filled in, this means that the numerator is normalized by an appropriate denominator at a specific timespan and geographic level. As you can see from all of the columns, measures can be specified in a large number of ways.

To search the metadata in a different way, we can also do more traditional keyword searches. Here we'll search the metadata for all measures from the '2011 - 2015' ACS 5-year Estimates that mentions 'education' by using a keyword search and matching with the geographic extent of your table.

```python
education_meta = cc.data_discovery(
    'taxi_50k',
    keywords='education',
    time='2011 - 2015'
)

# preview the data
education_meta.head()
```

To more fully inspect an entry, look at the values of a specific row:

```python
education_meta.iloc[0]
```

| denom_aggregate        |                                               sum |
| denom_colname          |                           population_3_years_over |
| denom_description      | The total number of people in each geography a... |
| denom_geomref_colname  |                                             geoid |
| denom_id               |                           us.census.acs.B14001001 |
| denom_name             |                       Population 3 Years and Over |
| denom_reltype          |                                       denominator |
| denom_t_description    |                                              None |
| denom_tablename        |      obs_77d6a9c06bd3511a6f89b594e7053a97d1c28f68 |
| denom_type             |                                           Numeric |
| geom_colname           |                                          the_geom |
| geom_description       | School Districts are geographic entities withi... |
| geom_geomref_colname   |                                             geoid |
| geom_id                |           us.census.tiger.school_district_unified |
| geom_name              |                           Unified School District |
| geom_t_description     |                                              None |
| geom_tablename         |      obs_d5cfd7148bd0d1d3522390caa79b3ccd427b1444 |
| geom_timespan          |                                              2015 |
| geom_type              |                                          Geometry |
| id                     |                                                 1 |
| max_score_rank         |                                              None |
| max_timespan_rank      |                                              None |
| normalization          |                                    predenominated |
| num_geoms              |                                           168.091 |
| numer_aggregate        |                                               sum |
| numer_colname          |                                         in_school |
| numer_description      | The total number of people in each geography c... |
| numer_geomref_colname  |                                             geoid |
| numer_id               |                           us.census.acs.B14001002 |
| numer_name             |                       Students Enrolled in School |
| numer_t_description    |                                              None |
| numer_tablename        |      obs_77d6a9c06bd3511a6f89b594e7053a97d1c28f68 |
| numer_timespan         |                                       2011 - 2015 |
| numer_type             |                                           Numeric |
| score                  |                                           41.1686 |
| score_rank             |                                                 1 |
| score_rownum           |                                                 1 |
| suggested_name         |                               in_school_2011_2015 |
| target_area            |                                              None |
| target_geoms           |                                              None |
| timespan_rank          |                                                 1 |
| timespan_rownum        |                                                 1 |

`Name: 0, dtype: object`

Or even filter further using pandas' `str` operations to find education measures that mention 'college':

```python
education_meta = education_meta[education_meta.numer_description.str.contains('college')]
education_meta.head()
```

### Augmenting your data

Once you have identified the correct metadata for the DO variables you want, you can augment an existing CARTO dataset and return it as a pandas DataFrame. There are two methods for passing in metadata to augment.

1. Pass the metadata DataFrame created from `cc.data_discovery` into `cc.data`

```python
median_income = cc.data_discovery('my_table',
                                  keyword='education',
                                  timespan='2011 - 2015')
df = cc.data('my_table',
             median_income_meta)
```

2. Or, you can pass in cherry-picked measures from the [Data Observatory catalog](https://cartodb.github.io/bigmetadata/index.html) as a list of dictionaries.  The rest of the metadata will be filled in, but it’s important to specify the geographic level.

```python
total_population = [{'numer_id': 'us.census.acs.B01003001',
                     'geom_id': 'us.census.tiger.block_group',
                     'numer_timespan': '2011 - 2015'}]
df = cc.data('my_table', total_population)
```

Additionally, you can persist the results as a new CARTO table by passing a new table name.

```python
df = cc.data(
    'my_table',
    total_population,
    persist_as='my_table_population'
)
```

### Accessing and finding boundaries

Using the `CartoContext.data_boundaries` method, you can find all the boundaries available in the world, in a country, or a region defined by the area of a table.

The following lists the metadata for all boundaries available in the DO:

```python
all_available_boundaries = cc.data_boundaries()
```

If you pass a boundary id, you will be returned with a table with a geometry id (`geom_refs`) and boundary geometries (`the_geom` in EWKB format). This query finds and returns all the boundaries for Australia Postal Areas:

```python
au_postal_areas = cc.data_boundaries(
    boundary='au.geo.POA'
)
```

We can also get the geometries decoded the EWKB geometries into [https://github.com/Toblerity/Shapely](Shapely geometries).

```python
au_postal_areas = cc.data_boundaries(
    boundary='au.geo.POA',
    decode_geom=True
)
```

### Getting raw measures and boundaries

Now let's start without any data and create a table with boundaries and their associated measures (raw or otherwise). One thing to note about boundaries in cartoframes: by default, US Census boundaries are shoreline-clipped. To disable this, set `include_nonclipped` to `True`.

In this example, we'll get the population density of all the US counties as of the 2015 ACS 1-year Estimates

```python
# find all US counties
us_counties = cc.data_boundaries(
    boundary='us.census.tiger.county',
    timespan='2015'
)

# write geometries to a CARTO table
cc.write(us_counties, 'us_counties')

# define metadata structure
# This can also be done with a CartoContext.data_discovery response
total_pop = [{'numer_id':'us.census.acs.B01003001',
              'geom_id':'us.census.tiger.county',
              'timespan':'2015 - 2015'}]

# augment dataset and persist as a new dataset
# use how='geom_refs' to get the raw measures
df = cc.data(
    'us_counties',
    total_pop,
    how='geom_refs'
)

# overwrite existing dataset
cc.write(df, 'us_counties', overwrite=True)

# create a choropleth map based on total population per square kilometer
cc.map(
    layers=QueryLayer(
        'SELECT * FROM us_counties WHERE total_pop_per_sq_km_2015_2015 < 1e4',
        color={'column': 'total_pop_per_sq_km_2015_2015',
               'scheme': styling.sunset(7)}
    ),
    interactive=True
)
```

![](../../img/guides/04-data-obs-pop-density.png)

One thing you'll notice about this map: rural areas tend to be null-valued (grey), while more populated areas show values. This is because the [US Census only includes areas with population greater than 65,000](https://www.census.gov/programs-surveys/acs/guidance/estimates.html) in the one year estimates.

### Getting boundaries for a specific region

To get measures for a specific region, it it sometimes required to first narrow down by geography and then filter by the `geom_refs` for the boundaries of interest.

Here we gather all census tracts for New York City:

```python
# request census tract geometry form us.census.tiger.census_tract
# filtered by the rough bounding box of New York City
tracts = cc.data_boundaries(
        boundary='us.census.tiger.census_tract',
        region=[-74.2589, 40.4774, -73.7004, 40.9176],
        timespan='2015')

# filtered by Federal Information Processing Standards (FIPS) County Code
# '36' is the FIPS code for New York State;
# '005', '047', '061', '081' and '085' are the FIPS codes for five boroughs in New York City
nyc_counties = ['36005', '36047', '36061', '36081', '36085']
nyc_ct = tracts[tracts.geom_refs.str[:5].isin(nyc_counties)]
```
