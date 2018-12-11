Cheatsheet
==========

How to get census tracts for a state and specific measures
----------------------------------------------------------

...

Get raw measures from the DO
----------------------------

Key part is to use `predenominated` in the metadata and `how='geoid'` (or some other geom_ref) when using `CartoContext.data`. Here we're using a dataset with a column called `geoid` which has the GEOID of census tracts. Note that it's important to specify the same geometry ID in the measure metadata as the geometries you are wishing to enrich.

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

   boston_data = cc.data('boston_census_tracts', meta, how='geoid')

Engineer your DO metadata if you already have GEOID or another geom_ref
-----------------------------------------------------------------------

Use `how='geom_ref_col'` and specify the appropriate boundary in the metadata.

How to get a matplotlib figure with four maps
---------------------------------------------

.. code::

   table = 'brooklyn_poverty'
   cols = [('pop_determined_poverty_status_2011_2015', 'Sunset'),
            ('poverty_per_pop', 'Mint'),
            ('walked_to_work_2011_2015', 'TealRose'),
            ('total_population', 'Peach')]

   fig, axs = plt.subplots(2, 2, figsize=(8, 8))

   for idx, col in enumerate(cols):
       cc.map(layers=[BaseMap('dark'), Layer(table,
                           color={'column': col[0],
                                  'scheme': styling.scheme(col[1], 7, 'quantiles')})],
              ax=axs[idx // 2][idx % 2],
              zoom=11, lng=-73.9476, lat=40.6437,
              interactive=False,
              size=(288, 288))
       axs[idx // 2][idx % 2].set_title(col[0])
   fig.tight_layout()
   plt.show()

.. image:: https://user-images.githubusercontent.com/1041056/35007309-42e818b6-fac7-11e7-87ab-b5148e011226.png

Get a GeoDataFrame
------------------

.. code::

   from cartoframes import CartoContext
   import geopandas as gpd
   cc = CartoContext()

   gdf = gpd.GeoDataFrame(cc.read('tablename', decode_geom=True))

Skip SSL verification
---------------------

.. code::

   from requests import Session
   session = Session()
   session.verify = False

   cc = CartoContext(base_url='...', api_key='...', session=session)

Reading large tables
--------------------

Sometimes tables are too large to read them out in a single `CartoContext.read` or `CartoContext.query` operation. In this case, you can read chunks and recombine, like below:

.. code::

   import pandas as pd
   dfs = []

   # template query
   q = '''
   SELECT * FROM my_big_table
   WHERE cartodb_id >= {lower} and cartodb_id < {upper}
   '''

   num_rows = cc.sql_client.send('select count(*) from my_big_table')['rows'][0]['count']

   # read in 100,000 chunks
   for r in range(0, num_rows, 100000):
       dfs.append(cc.query(q.format(lower=r, upper=r+100000)))
       
   # combine 'em all
   all_together = pd.concat(dfs)
   del dfs

When writing large DataFrames to CARTO, cartoframes takes care of the batching. Users shouldn't hit errors in general until they run out of size in the database.
