Cheat Sheet
===========

For most operations below, you need to create a :py:class:`DataObsClient <cartoframes.data.clients.DataObsClient>` object. For example, here's how user `cyclingfan` with API key `abc123` creates one:

.. code::

    from cartoframes.auth import Credentials
    from cartoframes.data.clients import DataObsClient

    credentials = Credentials(username='cyclingfan', api_key='abc123')
    do = DataObsClient(credentials)

How to get census tracts or counties for a state
------------------------------------------------

It's a fairly common use case that someone needs the Census tracts for a region. With cartoframes you have a lot of flexibility for obtaining this data.

1. Get bounding box of the region you're interested in. Tools like `Klockan's BoundingBox tool <https://boundingbox.klokantech.com/>`__ with the CSV output are prefect. Alternatively, use a table with the appropriate covering region (e.g., an existing table with polygon(s) of Missouri, its counties, etc.).
2. Get the FIPS code for the state(s) you're interested in. The US Census `provides a table <https://www.census.gov/geo/reference/ansi_statetables.html>`__ as do many other sites. In this case, I'm choosing ``29`` for Missouri.

.. code::

    from cartoframes.data import Dataset
    from cartoframes.viz import Map, Layer


    # get all census tracts (clipped by water boundaries) in specific bounding box
    missouri_ct_dataset = do.boundaries(
        region=[-95.774147,35.995682,-89.098846,40.613636],
        boundary='us.census.tiger.census_tract_clipped'
    )

    # get dataframe
    df = missouri_ct_dataset.dataframe

    # filter out all census tracts that begin with Missouri FIPS (29)
    # GEOIDs begin with two digit state FIPS, followed by three digit county FIPS
    missouri_ct_dataframe = df[df.geom_refs.str.startswith('29')]

    # write to carto
    ds = Dataset(missouri_ct_dataframe)
    ds.upload(table_name='missouri_census_tracts', credentials=credentials)

    # visualize to make sure it makes sense
    Map(Layer(ds))


.. image:: img/cheatsheet_do_census_tracts.png
   :alt: Map with census tracts of Missouri

Since `pandas.Series.str.startswith` can take multiple string prefixes, we can filter for more than one state at a time. In this case, get all Missouri and Kansas counties:

.. code::

    from cartoframes.data import Dataset
    from cartoframes.viz import Map, Layer


    # get all counties in bounding box around Kansas and Missouri
    ks_mo_counties_dataset = do.boundaries(
        region=[-102.1777729674,35.995682,-89.098846,40.613636],
        boundary='us.census.tiger.county'
    )

    # get dataframe
    df = ks_mo_counties_dataset.dataframe

    # filter out all counties that begin with Missouri (29) or Kansas (20) FIPS
    ks_mo_counties = df[df.geom_refs.str.startswith(('29', '20'))]

    # write to carto
    ds = Dataset(ks_mo_counties)
    ds.upload(table_name='ks_mo_counties', credentials=credentials)

    # visualize to make sure it makes sense
    Map(Layer(ds))


.. image:: img/cheatsheet_do_counties.png
   :alt: Map with counties for Kansas and Missouri

Get raw measures from the DO
----------------------------

To get raw census measures from the Data Observatory, the key part is the use of `predenominated` in the metadata and `how='geoid'` (or some other geom_ref) when using `DataObsClient.augment`. If you don't use the `how=` flag, the Data Observatory will perform some calculations with the geometries in the table you are trying to augment.

Here we're using a dataset with a column called `geoid` which has the GEOID of census tracts. Note that it's important to specify the same geometry ID in the measure metadata as the geometries you are wishing to enrich.

1. Find the measures you want, either through `DataObsClient.discovery` or using the `Data Observatory catalog <https://cartodb.github.io/bigmetadata/>`__.
2. Create a dataframe with columns for each measure metadata object, or a list of dictionaries (like below) for your curated measures. Be careful to specify the specific geometry level you want the measures for and make sure the geometry reference (e.g., GEOID) you have for your geometries matches this geometry level.


.. code::

   # get median income for 2006 - 2010 and 2011 - 2015 five year estimates.
    meta = [{
        'numer_id': 'us.census.acs.B19013001',
        'geom_id': 'us.census.tiger.census_tract',
        'normalization': 'predenominated',
        'numer_timespan': '2006 - 2010'
    }, {
        'numer_id': 'us.census.acs.B19013001',
        'geom_id': 'us.census.tiger.census_tract',
        'normalization': 'predenominated',
        'numer_timespan': '2011 - 2015'
    }]

    boston_data = do.augment('boston_census_tracts', meta, how='geoid')


.. tip:: It's best practice to keep your geometry identifiers as strings because leading zeros are removed when strings are converted to numeric types. This usually affects states with FIPS that begin with a zero, or Zip Codes in New England with leading zeros.

Engineer your DO metadata if you already have GEOID or another geom_ref
-----------------------------------------------------------------------

Use `how='geom_ref_col'` and specify the appropriate boundary in the metadata.


Get a table as a GeoDataFrame
-----------------------------

CARTOframes works with GeoPandas.

You can create a :py:class:`Dataset <cartoframes.data.Dataset>` instance from a GeoDataFrame:

.. code::

    from geopandas
    from cartoframes.data import Dataset
    from cartoframes.auth import Credentials
    from cartoframes.viz import Map, Layer

    gdf = geopandas.DataFrame(...)
    ds = Dataset(gdf)

    # save data in CARTO
    credentials = Credentials(username='<USER NAME>', api_key='<API KEY>')
    ds.upload(table_name='table_name', credentials=credentials)

    # create a MAP
    Map(Layer(ds))

To convert the data from a CARTO table into a GeoPandas GeoDataFrame:

1. Call Dataset.download using the `decode_geom` flag set to ``True``, like below.
2. Wrap the result of step 1 in the GeoPandas GeoDataFrame constructor

Your new GeoDataFrame will now have geometries decoded into Shapely objects that can then be used for spatial operations in your Python environment.

.. code::

    from cartoframes.auth import Credentials
    from cartoframes.data import Dataset

    credentials = Credentials(username='<USER NAME>', api_key='<API KEY>')

    dataframe = Dataset('your_table', credentials=credentials).download(decode_geom=True)

    gdf = gpd.GeoDataFrame(dataframe)


Skip SSL verification
---------------------

Some `on premises installations of CARTO <https://carto.com/developers/on-premises/>`__ don't need SSL verification. You can disable this using the requests library's `Session class <http://docs.python-requests.org/en/master/user/advanced/#session-objects>`__ and passing that into your :py:class:`Credentials <cartoframes.auth.Credentials>`.

.. code::

    from requests import Session
    session = Session()
    session.verify = False

    credentials = Credentials(
        username='<USER NAME>',
        api_key='<API KEY>',
        session=session)


Perform long running query if a timeout occurs
-----------------------------------------------

In order to run a long running query, CARTO has the
`Batch API <https://carto.com/developers/sql-api/reference/#tag/Batch-Queries>`.
Below is a sample workflow for how to perform a long running query that would otherwise produce timeout errors.

.. code::

    from cartoframes.auth import Credentials
    from cartoframes.data.clients import SQLClient

    credentials = Credentials(username='<USER NAME>', api_key='<API KEY>')
    sql = SQLClient(credentials)

    sql.execute('<LONG RUNNING QUERY>')


Subdivide Data Observatory search region into sub-regions
---------------------------------------------------------

Some geometries in the Data Observatory are too large, numerous, and/or complex to retrieve in one request. Census tracts (especially if they are shoreline-clipped) is one popular example. To retrieve this data, it helps to first break the search region into subregions, collect the data in each of the subregions, and then combine the data at the end. To avoid duplicate geometries along the sub-region edges, we apply the `DataFrame.drop_duplicates` method for the last step.

.. code::

    import itertools

    # bbox that encompasses lower 48 states of USA
    bbox = [
        -126.8220242454,
        22.991640246,
        -64.35549002,
        51.5559807141
    ]

    # make these numbers larger if the sub-regions are not small enough
    # make these numbers smaller to get more data in one call
    num_divs_lng = 5
    num_divs_lat = 3

    delta_lng_divs = (bbox[2] - bbox[0]) / num_divs_lng
    delta_lat_divs = (bbox[3] - bbox[1]) / num_divs_lat

    sub_data = []
    for p in itertools.product(range(num_divs_lng), range(num_divs_lat)):
        sub_bbox = (
            bbox[0] + p[0] * delta_lng_divs,
            bbox[1] + p[1] * delta_lat_divs,
            bbox[0] + (p[0] + 1) * delta_lng_divs,
            bbox[1] + (p[1] + 1) * delta_lat_divs
        )
        _df = do.boundaries(
            region=sub_bbox,
            boundary='us.census.tiger.census_tract_clipped'
        )
        sub_data.append(_df)

    df_all = pd.concat(sub_data)[['geom_refs', 'the_geom']]
    df_all.drop_duplicates(inplace=True)
    del sub_data
