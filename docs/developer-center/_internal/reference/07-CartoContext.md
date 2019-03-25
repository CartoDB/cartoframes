
### CartoContext

_class_ `cartoframes.context.CartoContext(base_url=None, api_key=None, creds=None, session=None, verbose=0)`

CartoContext class for authentication with CARTO and high-level operations such as reading tables from CARTO into dataframes, writing dataframes to CARTO tables, creating custom maps from dataframes and CARTO tables, and augmenting data using CARTO’s [Data Observatory](https://carto.com/data-observatory). Future methods will interact with CARTO’s services like [routing, geocoding, and isolines](https://carto.com/location-data-services/), PostGIS backend for spatial processing, and much more.

Manages connections with CARTO for data and map operations. Modeled after [SparkContext](http://spark.apache.org/docs/2.1.0/api/python/pyspark.html#pyspark.SparkContext).

There are two ways of authenticating against a CARTO account:

1.  Setting the `base_url` and `api_key` directly in CartoContext. This method is easier.:
    ```python
    cc = CartoContext(
        base_url='https://eschbacher.carto.com',
        api_key='abcdefg')
    ```

2.  By passing a `Credentials` instance in CartoContext’s creds keyword argument. This method is more flexible.:

    ```python
    from cartoframes import Credentials
    creds = Credentials(username='eschbacher', key='abcdefg')
    cc = CartoContext(creds=creds)
    ```


Attributes:

* **creds** [¶](#cartoframes.context.CartoContext.creds "Permalink to this definition") - `Credentials` – `Credentials` instance

Parameters:

*   **base\_url** (_str_) – Base URL of CARTO user account. Cloud-based accounts should use the form `https://{username}.carto.com` (e.g., [https://eschbacher.carto.com](https://eschbacher.carto.com) for user `eschbacher`) whether on a personal or multi-user account. On-premises installation users should ask their admin.
*   **api_key** (_str_) – CARTO API key.
*   **creds** (`Credentials`) – A `Credentials` instance can be used in place of a base_url/api_key combination.
*   **session** (_requests.Session__,_ _optional_) – requests session. See [requests documentation](http://docs.python-requests.org/en/master/user/advanced/) for more information.
*   **verbose** (_bool__,_ _optional_) – Output underlying process states (True), or suppress (False, default)

Returns:

A CartoContext object that is authenticated against the user’s CARTO account.

Return type:

[`CartoContext`](cartoframes.context.html#cartoframes.context.CartoContext "cartoframes.context.CartoContext")

Example

Create a CartoContext object:

```python
import cartoframes
cc = cartoframes.CartoContext(BASEURL, APIKEY)
```

`write`(df, table\_name, temp\_dir=SYSTEM\_TMP\_PATH, overwrite=False, lnglat=None, encode\_geom=False, geom\_col=None, \*\*kwargs)[¶](#cartoframes.context.CartoContext.write "Permalink to this definition")

Write a DataFrame to a CARTO table.

Examples

Write a pandas DataFrame to CARTO.

cc.write(df, 'brooklyn_poverty', overwrite=True)

Scrape an HTML table from Wikipedia and send to CARTO with content guessing to create a geometry from the country column. This uses a CARTO Import API param content_guessing parameter.

url = 'https://en.wikipedia.org/wiki/List\_of\_countries\_by\_life_expectancy'
\# retrieve first HTML table from that page
df = pd.read_html(url, header=0)\[0\]
\# send to carto, let it guess polygons based on the 'country'
\#   column. Also set privacy to 'public'
cc.write(df, 'life_expectancy',
         content_guessing=True,
         privacy='public')
cc.map(layers=Layer('life_expectancy',
                    color='both\_sexes\_life_expectancy'))



Parameters:

*   **df** (_pandas.DataFrame_) – DataFrame to write to `table_name` in user CARTO account
*   **table_name** (_str_) – Table to write `df` to in CARTO.
*   **temp_dir** (_str__,_ _optional_) – Directory for temporary storage of data that is sent to CARTO. Defaults are defined by [appdirs](https://github.com/ActiveState/appdirs/blob/master/README.rst).
*   **overwrite** (_bool__,_ _optional_) – Behavior for overwriting `table_name` if it exits on CARTO. Defaults to `False`.
*   **lnglat** (_tuple__,_ _optional_) – lng/lat pair that can be used for creating a geometry on CARTO. Defaults to `None`. In some cases, geometry will be created without specifying this. See CARTO’s [Import API](https://carto.com/docs/carto-engine/import-api/standard-tables) for more information.
*   **encode_geom** (_bool__,_ _optional_) – Whether to write geom_col to CARTO as the_geom.
*   **geom_col** (_str__,_ _optional_) – The name of the column where geometry information is stored. Used in conjunction with encode_geom.
*   ****kwargs** –

    Keyword arguments to control write operations. Options are:

    *   compression to set compression for files sent to CARTO. This will cause write speedups depending on the dataset. Options are `None` (no compression, default) or `gzip`.
    *   Some arguments from CARTO’s Import API. See the [params listed in the documentation](https://carto.com/docs/carto-engine/import-api/standard-tables/#params) for more information. For example, when using content_guessing=’true’, a column named ‘countries’ with country names will be used to generate polygons for each country. Another use is setting the privacy of a dataset. To avoid unintended consequences, avoid file, url, and other similar arguments.

Returns:

If lnglat flag is set and the DataFrame has more than 100,000 rows, a [`BatchJobStatus`](cartoframes.context.html#cartoframes.context.BatchJobStatus "cartoframes.context.BatchJobStatus") instance is returned. Otherwise, None.

Return type:

[`BatchJobStatus`](cartoframes.context.html#cartoframes.context.BatchJobStatus "cartoframes.context.BatchJobStatus") or None

Note

DataFrame indexes are changed to ordinary columns. CARTO creates an index called cartodb_id for every table that runs from 1 to the length of the DataFrame.

`read`(_table_name_, _limit=None_, _index='cartodb_id'_, _decode_geom=False_, _shared_user=None_)

Read a table from CARTO into a pandas DataFrames.



Parameters:

*   **table_name** (_str_) – Name of table in user’s CARTO account.
*   **limit** (_int__,_ _optional_) – Read only limit lines from table_name. Defaults to `None`, which reads the full table.
*   **index** (_str__,_ _optional_) – Not currently in use.
*   **decode_geom** (_bool__,_ _optional_) – Decodes CARTO’s geometries into a [Shapely](https://github.com/Toblerity/Shapely) object that can be used, for example, in [GeoPandas](http://geopandas.org/).
*   **shared_user** (_str__,_ _optional_) – If a table has been shared with you, specify the user name (schema) who shared it.

Returns:

DataFrame representation of table_name from CARTO.

Return type:

pandas.DataFrame

Example

import cartoframes
cc = cartoframes.CartoContext(BASEURL, APIKEY)
df = cc.read('acadia_biodiversity')

`delete`(_table_name_)

Delete a table in user’s CARTO account.



Parameters:

**table_name** (_str_) – Name of table to delete

Returns:

None

`query`(_query_, _table_name=None_, _decode_geom=False_)

Pull the result from an arbitrary SQL query from a CARTO account into a pandas DataFrame. Can also be used to perform database operations (creating/dropping tables, adding columns, updates, etc.).



Parameters:

*   **query** (_str_) – Query to run against CARTO user database. This data will then be converted into a pandas DataFrame.
*   **table_name** (_str__,_ _optional_) – If set, this will create a new table in the user’s CARTO account that is the result of the query. Defaults to None (no table created).
*   **decode_geom** (_bool__,_ _optional_) – Decodes CARTO’s geometries into a [Shapely](https://github.com/Toblerity/Shapely) object that can be used, for example, in [GeoPandas](http://geopandas.org/).

Returns:

DataFrame representation of query supplied. Pandas data types are inferred from PostgreSQL data types. In the case of PostgreSQL date types, dates are attempted to be converted, but on failure a data type ‘object’ is used.

Return type:

pandas.DataFrame

`map`(_layers=None_, _interactive=True_, _zoom=None_, _lat=None_, _lng=None_, _size=(800_, _400)_, _ax=None_)

Produce a CARTO map visualizing data layers.

Examples

Create a map with two data layers, and one BaseMap layer:

import cartoframes
from cartoframes import Layer, BaseMap, styling
cc = cartoframes.CartoContext(BASEURL, APIKEY)
cc.map(layers=\[BaseMap(),
               Layer('acadia_biodiversity',
                     color={'column': 'simpson_index',
                            'scheme': styling.tealRose(7)}),
               Layer('peregrine\_falcon\_nest_sites',
                     size='num_eggs',
                     color={'column': 'bird_id',
                            'scheme': styling.vivid(10))\],
       interactive=True)

Create a snapshot of a map at a specific zoom and center:

cc.map(layers=Layer('acadia_biodiversity',
                    color='simpson_index'),
       interactive=False,
       zoom=14,
       lng=-68.3823549,
       lat=44.3036906)



Parameters:

*   **layers** (_list__,_ _optional_) –

    List of one or more of the following:

    *   Layer: cartoframes Layer object for visualizing data from a CARTO table. See [layer.Layer](#layer.Layer) for all styling options.
    *   BaseMap: Basemap for contextualizng data layers. See [layer.BaseMap](#layer.BaseMap) for all styling options.
    *   QueryLayer: Layer from an arbitrary query. See [layer.QueryLayer](#layer.QueryLayer) for all styling options.
*   **interactive** (_bool__,_ _optional_) – Defaults to `True` to show an interactive slippy map. Setting to `False` creates a static map.
*   **zoom** (_int__,_ _optional_) – Zoom level of map. Acceptable values are usually in the range 0 to 19. 0 has the entire earth on a single tile (256px square). Zoom 19 is the size of a city block. Must be used in conjunction with `lng` and `lat`. Defaults to a view to have all data layers in view.
*   **lat** (_float__,_ _optional_) – Latitude value for the center of the map. Must be used in conjunction with `zoom` and `lng`. Defaults to a view to have all data layers in view.
*   **lng** (_float__,_ _optional_) – Longitude value for the center of the map. Must be used in conjunction with `zoom` and `lat`. Defaults to a view to have all data layers in view.
*   **size** (_tuple__,_ _optional_) – List of pixel dimensions for the map. Format is `(width, height)`. Defaults to `(800, 400)`.
*   **ax** – matplotlib axis on which to draw the image. Only used when `interactive` is `False`.

Returns:

Interactive maps are rendered as HTML in an iframe, while static maps are returned as matplotlib Axes objects or IPython Image.

Return type:

IPython.display.HTML or matplotlib Axes

`data_boundaries`(_boundary=None_, _region=None_, _decode_geom=False_, _timespan=None_, _include_nonclipped=False_)

Find all boundaries available for the world or a region. If boundary is specified, get all available boundary polygons for the region specified (if any). This method is espeically useful for getting boundaries for a region and, with CartoContext.data and CartoContext.data_discovery, getting tables of geometries and the corresponding raw measures. For example, if you want to analyze how median income has changed in a region (see examples section for more).

Examples

Find all boundaries available for Australia. The columns geom_name gives us the name of the boundary and geom_id is what we need for the boundary argument.

import cartoframes
cc = cartoframes.CartoContext('base url', 'api key')
au_boundaries = cc.data_boundaries(region='Australia')
au_boundaries\[\['geom_name', 'geom_id'\]\]

Get the boundaries for Australian Postal Areas and map them.

from cartoframes import Layer
au\_postal\_areas = cc.data_boundaries(boundary='au.geo.POA')
cc.write(au\_postal\_areas, 'au\_postal\_areas')
cc.map(Layer('au\_postal\_areas'))

Get census tracts around Idaho Falls, Idaho, USA, and add median income from the US census. Without limiting the metadata, we get median income measures for each census in the Data Observatory.

cc = cartoframes.CartoContext('base url', 'api key')
\# will return DataFrame with columns \`the\_geom\` and \`geom\_ref\`
tracts = cc.data_boundaries(
    boundary='us.census.tiger.census_tract',
    region=\[-112.096642,43.429932,-111.974213,43.553539\])
\# write geometries to a CARTO table
cc.write(tracts, 'idaho\_falls\_tracts')
\# gather metadata needed to look up median income
median\_income\_meta = cc.data_discovery(
    'idaho\_falls\_tracts',
    keywords='median income',
    boundaries='us.census.tiger.census_tract')
\# get median income data and original table as new dataframe
idaho\_falls\_income = cc.data(
    'idaho\_falls\_tracts',
    median\_income\_meta,
    how='geom_refs')
\# overwrite existing table with newly-enriched dataframe
cc.write(idaho\_falls\_income,
         'idaho\_falls\_tracts',
         overwrite=True)



Parameters:

*   **boundary** (_str__,_ _optional_) – Boundary identifier for the boundaries that are of interest. For example, US census tracts have a boundary ID of `us.census.tiger.census_tract`, and Brazilian Municipios have an ID of `br.geo.municipios`. Find IDs by running CartoContext.data_boundaries without any arguments, or by looking in the [Data Observatory catalog](http://cartodb.github.io/bigmetadata/).
*   **region** (_str__,_ _optional_) –

    Region where boundary information or, if boundary is specified, boundary polygons are of interest. region can be one of the following:

    > *   table name (str): Name of a table in user’s CARTO account
    > *   bounding box (list of float): List of four values (two lng/lat pairs) in the following order: western longitude, southern latitude, eastern longitude, and northern latitude. For example, Switzerland fits in `[5.9559111595,45.8179931641,10.4920501709,47.808380127]`

*   **timespan** (_str__,_ _optional_) – Specific timespan to get geometries from. Defaults to use the most recent. See the Data Observatory catalog for more information.
*   **decode_geom** (_bool__,_ _optional_) – Whether to return the geometries as Shapely objects or keep them encoded as EWKB strings. Defaults to False.
*   **include_nonclipped** (_bool__,_ _optional_) – Optionally include non-shoreline-clipped boundaries. These boundaries are the raw boundaries provided by, for example, US Census Tiger.

Returns:

If boundary is specified, then all available boundaries and accompanying geom_refs in region (or the world if region is `None` or not specified) are returned. If boundary is not specified, then a DataFrame of all available boundaries in region (or the world if region is `None`)

Return type:

pandas.DataFrame

`data_discovery`(_region_, _keywords=None_, _regex=None_, _time=None_, _boundaries=None_, _include_quantiles=False_)

Discover Data Observatory measures. This method returns the full Data Observatory metadata model for each measure or measures that match the conditions from the inputs. The full metadata in each row uniquely defines a measure based on the timespan, geographic resolution, and normalization (if any). Read more about the metadata response in [Data Observatory](https://carto.com/docs/carto-engine/data/measures-functions/#obs_getmetaextent-geometry-metadata-json-max_timespan_rank-max_score_rank-target_geoms) documentation.

Internally, this method finds all measures in region that match the conditions set in keywords, regex, time, and boundaries (if any of them are specified). Then, if boundaries is not specified, a geographical resolution for that measure will be chosen subject to the type of region specified:

> 1.  If region is a table name, then a geographical resolution that is roughly equal to region size / number of subunits.
> 2.  If region is a country name or bounding box, then a geographical resolution will be chosen roughly equal to region size / 500.

Since different measures are in some geographic resolutions and not others, different geographical resolutions for different measures are oftentimes returned.

Tip

To remove the guesswork in how geographical resolutions are selected, specify one or more boundaries in boundaries. See the boundaries section for each region in the [Data Observatory catalog](http://cartodb.github.io/bigmetadata/).

The metadata returned from this method can then be used to create raw tables or for augmenting an existing table from these measures using CartoContext.data. For the full Data Observatory catalog, visit [https://cartodb.github.io/bigmetadata/](https://cartodb.github.io/bigmetadata/). When working with the metadata DataFrame returned from this method, be careful to only remove rows not columns as [CartoContext.data](#context.CartoContext.data) generally needs the full metadata.

Note

Narrowing down a discovery query using the keywords, regex, and time filters is important for getting a manageable metadata set. Besides there being a large number of measures in the DO, a metadata response has acceptable combinations of measures with demonimators (normalization and density), and the same measure from other years.

For example, setting the region to be United States counties with no filter values set will result in many thousands of measures.

Examples

Get all European Union measures that mention `freight`.

meta = cc.data_discovery('European Union',
                         keywords='freight',
                         time='2010')
print(meta\['numer_name'\].values)



Parameters:

*   **region** (_str_ _or_ _list of float_) –

    Information about the region of interest. region can be one of three types:

    > *   region name (str): Name of region of interest. Acceptable values are limited to: ‘Australia’, ‘Brazil’, ‘Canada’, ‘European Union’, ‘France’, ‘Mexico’, ‘Spain’, ‘United Kingdom’, ‘United States’.
    > *   table name (str): Name of a table in user’s CARTO account with geometries. The region will be the bounding box of the table.
    >
    >     Note
    >
    >     If a table name is also a valid Data Observatory region name, the Data Observatory name will be chosen over the table.
    >
    > *   bounding box (list of float): List of four values (two lng/lat pairs) in the following order: western longitude, southern latitude, eastern longitude, and northern latitude. For example, Switzerland fits in `[5.9559111595,45.8179931641,10.4920501709,47.808380127]`
    >
    > Note
    >
    > Geometry levels are generally chosen by subdividing the region into the next smallest administrative unit. To override this behavior, specify the boundaries flag. For example, set boundaries to `'us.census.tiger.census_tract'` to choose US census tracts.

*   **keywords** (_str_ _or_ _list of str__,_ _optional_) – Keyword or list of keywords in measure description or name. Response will be matched on all keywords listed (boolean or).
*   **regex** (_str__,_ _optional_) – A regular expression to search the measure descriptions and names. Note that this relies on PostgreSQL’s case insensitive operator `~*`. See [PostgreSQL docs](https://www.postgresql.org/docs/9.5/static/functions-matching.html) for more information.
*   **boundaries** (_str_ _or_ _list of str__,_ _optional_) – Boundary or list of boundaries that specify the measure resolution. See the boundaries section for each region in the [Data Observatory catalog](http://cartodb.github.io/bigmetadata/).
*   **include_quantiles** (_bool__,_ _optional_) – Include quantiles calculations which are a calculation of how a measure compares to all measures in the full dataset. Defaults to `False`. If `True`, quantiles columns will be returned for each column which has it pre-calculated.

Returns:

A dataframe of the complete metadata model for specific measures based on the search parameters.

Return type:

pandas.DataFrame

Raises:

*   `ValueError` – If region is a `list` and does not consist of four elements, or if region is not an acceptable region
*   `CartoException` – If region is not a table in user account

`data`(_table_name_, _metadata_, _persist_as=None_, _how='the_geom'_)

Get an augmented CARTO dataset with [Data Observatory](https://carto.com/data-observatory) measures. Use [CartoContext.data_discovery](#context.CartoContext.data_discovery) to search for available measures, or see the full [Data Observatory catalog](https://cartodb.github.io/bigmetadata/index.html). Optionally persist the data as a new table.

Example

Get a DataFrame with Data Observatory measures based on the geometries in a CARTO table.

cc = cartoframes.CartoContext(BASEURL, APIKEY)
median_income = cc.data_discovery('transaction_events',
                                  regex='.\*median income.\*',
                                  time='2011 - 2015')
df = cc.data('transaction_events',
             median_income)

Pass in cherry-picked measures from the Data Observatory catalog. The rest of the metadata will be filled in, but it’s important to specify the geographic level as this will not show up in the column name.

median_income = \[{'numer_id': 'us.census.acs.B19013001',
                  'geom_id': 'us.census.tiger.block_group',
                  'numer_timespan': '2011 - 2015'}\]
df = cc.data('transaction_events', median_income)



Parameters:

*   **table_name** (_str_) – Name of table on CARTO account that Data Observatory measures are to be added to.
*   **metadata** (_pandas.DataFrame_) – List of all measures to add to table_name. See CartoContext.data_discovery outputs for a full list of metadata columns.
*   **persist_as** (_str__,_ _optional_) – Output the results of augmenting table_name to persist_as as a persistent table on CARTO. Defaults to `None`, which will not create a table.
*   **how** (_str__,_ _optional_) – **Not fully implemented**. Column name for identifying the geometry from which to fetch the data. Defaults to the_geom, which results in measures that are spatially interpolated (e.g., a neighborhood boundary’s population will be calculated from underlying census tracts). Specifying a column that has the geometry identifier (for example, GEOID for US Census boundaries), results in measures directly from the Census for that GEOID but normalized how it is specified in the metadata.

Returns:

A DataFrame representation of table_name which has new columns for each measure in metadata.

Return type:

pandas.DataFrame

Raises:

*   `NameError` – If the columns in table_name are in the `suggested_name` column of metadata.
*   `ValueError` – If metadata object is invalid or empty, or if the number of requested measures exceeds 50.
*   `CartoException` – If user account consumes all of Data Observatory quota
