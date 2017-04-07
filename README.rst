CARTOFrames
===========

A pandas interface for integrating `CARTO <https://carto.com/>`__ into data science workflows.

Python data analysis workflows often rely on the de facto standards `pandas <http://pandas.pydata.org/>`__ and `Jupyter notebooks <http://jupyter.org/>`__. Integrating CARTO into this workflow saves data scientists time and energy by not having to export datasets as files or retain multiple copies of the data. Instead, CARTOFrames give the ability to communicate reproducible analysis while providing the ability to gain from CARTO's services like hosted, dynamic or static maps and `Data Observatory <https://carto.com/data-observatory/>`__ augmentation.

Install Instructions
--------------------

`cartoframes` relies on `pandas <http://pandas.pydata.org/>`__ and a development version of the CARTO Python SDK (on branch `1.0.0 <https://github.com/CartoDB/carto-python/tree/1.0.0>`__). To install `cartoframes` on your machine, do the following:

1. Clone this repository.

2. Change your directory to `cartoframes` and run the following:

.. code:: bash

    $ pip install -r requirements.txt
    $ pip install cartoframes

Once you've done this, `cartoframes` will be installed. See the example usage section below for using cartoframes in a Jupyter notebook.

Note: Eventually `cartoframes` will be fully installable from `pip`.


Example usage
-------------

Data workflow
~~~~~~~~~~~~~

Get table from carto, make changes in pandas, sync updates with carto:

.. code:: python

    df = pd.read_carto(username=username,
                       api_key=api_key,
                       tablename='brooklyn_poverty_census_tracts')
    # do fancy pandas operations (add/drop columns, change values, etc.)
    df['poverty_per_pop'] = df['poverty_count'] / df['total_population']

    # updates carto table with all changes from this session
    # show all database access with debug=True
    df.sync_carto()

.. figure:: https://raw.githubusercontent.com/CartoDB/cartoframes/master/examples/read_carto.png
   :alt: Example of creating a fresh cartoframe, performing an operation, and syncing with carto


Associate an existing pandas dataframe with CARTO, and optionally get the geometry.

.. code:: python

    import pandas as pd
    import cartoframes
    import numpy as np
    arr = np.arange(10)
    np.random.shuffle(arr)
    ingest = {'ids': list('abcdefghij'),
              'scores': np.random.random(10),
              'other_rank': arr,
              'lat': 40.7128 + (0.5 - np.random.random(10)),
              'lon': -74.0059 + (0.5 - np.random.random(10))}
    df = pd.DataFrame(ingest)
    df.sync_carto(username=USERNAME,
                  api_key=APIKEY,
                  requested_tablename='awesome_new_table',
                  createtable=True,
                  is_org_user=True,
                  latlng_cols=('lat', 'lon'))

.. figure:: https://raw.githubusercontent.com/CartoDB/cartoframes/master/examples/create_carto.png
   :alt: Example of creating a fresh cartoframe, performing an operation, and syncing with carto


Map workflow
~~~~~~~~~~~~

The following will embed a CARTO map in a Jupyter notebook, allowing for custom styling of the maps driving by `Turbo Carto <https://github.com/CartoDB/turbo-carto>`__ and `CartoColors <https://carto.com/blog/introducing-cartocolors>`__.

.. code:: python

    df.carto_map(color={'colname': 'net', 'ramp': 'Bold'},
                 size={'colname': 'depth', 'min': 6, 'max': 20, 'quant_method': 'headtails'},
                 basemap='http://{s}.tile.thunderforest.com/spinal-map/{z}/{x}/{y}.png')

.. figure:: https://raw.githubusercontent.com/CartoDB/cartoframes/master/examples/carto_map.png
   :alt: Example of creating a cartoframe map in a Jupyter notebook

Augment from Data Observatory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Interact with CARTO's Data Observatory:

.. code:: python

    # total pop, high school diploma (normalized), median income, poverty status (normalized)
    # See Data Observatory catalog for codes: https://cartodb.github.io/bigmetadata/index.html
    data_obs_measures = [{'numer_id': 'us.census.acs.B01003001'},
                         {'numer_id': 'us.census.acs.B15003017', 'denominator': 'predenominated'},
                         {'numer_id': 'us.census.acs.B19013001'},
                         {'numer_id': 'us.census.acs.B17001002', 'denominator': 'predenominated'}]
    df.carto_do_augment(data_obs_measures)
    df.head()

.. figure:: https://raw.githubusercontent.com/CartoDB/cartoframes/master/examples/data_obs_augmentation.png
   :alt: Example of using data observatory augmentation methods
