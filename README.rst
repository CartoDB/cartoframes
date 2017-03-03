CartoFrames
===========

A pandas interface for integrating `Carto <https://carto.com/>`__ into a
data science workflow.

Install Instructions
--------------------

`cartoframes` relies on `pandas <http://pandas.pydata.org/>`__ and a development version of the CARTO Python SDK (on branch `1.0.0 <https://github.com/CartoDB/carto-python/tree/1.0.0>`__). To install `cartoframes` on your machine, do the following:

Copy the requirements.txt file in this repo to your machine and run:

.. code:: bash

    $ pip install -r requirements.txt
    $ pip install pyrestcli

Next, install `cartoframes` through `pip`:

.. code:: bash

    $ pip install cartoframes

Once you've done this, `cartoframes` should be installed on your machine. See the example usage section below for using cartoframes in a Jupyter notebook.

Note: Eventually `cartoframes` will be fully installable from `pip`.


Example usage
-------------

Data workflow
~~~~~~~~~~~~~

Get table from carto, make changes in pandas, sync updates with carto:

.. code:: python

    import pandas as pd
    import cartoframes
    username = 'eschbacher'
    api_key = 'abcdefghijklmnopqrstuvwxyz'
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
    df.carto_create('eschbacher',
                    '05a458d3a45d1237699a4ee05297bb92accce3f4',
                    'awesome_new_table',
                    is_org_user=True, latlng_cols=('lat', 'lon'))

.. figure:: https://raw.githubusercontent.com/CartoDB/cartoframes/master/examples/create_carto.png
   :alt: Example of creating a fresh cartoframe, performing an operation, and syncing with carto


Map workflow
~~~~~~~~~~~~

The following will embed a CARTO map in a Jupyter notebook (interactive
or static).

.. code:: python

    df = pd.read_carto(username=username,
                       api_key=api_key,
                       tablename='brooklyn_poverty_census_tracts')
    df.carto_map(interactive=True, stylecol='poverty_per_pop')

.. figure:: https://raw.githubusercontent.com/CartoDB/cartoframes/master/examples/data_obs_augmentation.png
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
