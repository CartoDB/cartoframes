CARTOFrames
===========

.. image:: https://travis-ci.org/CartoDB/cartoframes.svg?branch=master
    :target: https://travis-ci.org/CartoDB/cartoframes

A Python package for integrating `CARTO <https://carto.com/>`__ maps and services into data science workflows.

Python data analysis workflows often rely on the de facto standards `pandas <http://pandas.pydata.org/>`__ and `Jupyter notebooks <http://jupyter.org/>`__. Integrating CARTO into this workflow saves data scientists time and energy by not having to export datasets as files or retain multiple copies of the data. Instead, CARTOFrames give the ability to communicate reproducible analysis while providing the ability to gain from CARTO's services like hosted, dynamic or static maps and `Data Observatory <https://carto.com/data-observatory/>`__ augmentation.

Complete documentation: https://cartodb.github.io/cartoframes/

Install Instructions
--------------------

`cartoframes` relies on `pandas <http://pandas.pydata.org/>`__ and the `CARTO Python SDK <https://github.com/CartoDB/carto-python/>`__). To install `cartoframes` on your machine, do the following:

.. code:: bash

    $ pip install cartoframes

Once you've done this, `cartoframes` will be installed. See the example usage section below for using `cartoframes` in a Jupyter notebook. **User must have a CARTO API key for writing DataFrames to an account or reading from private tables.**

**Note:** Eventually `cartoframes` will be fully installable from `pip`.


Example usage
-------------

Data workflow
~~~~~~~~~~~~~

Get table from CARTO, make changes in pandas, sync updates with CARTO:

.. code:: python

    import cartoframes
    # `base_url`s are of the form `http://{username}.carto.com/` for most users
    cc = cartoframes.CartoContext(base_url='https://eschbacher.carto.com/',
                                  api_key=APIKEY)

    # read a table from your CARTO account to a DataFrame
    df = cc.read('brooklyn_poverty_census_tracts')

    # do fancy pandas operations (add/drop columns, change values, etc.)
    df['poverty_per_pop'] = df['poverty_count'] / df['total_population']

    # updates CARTO table with all changes from this session
    cc.write(df, 'brooklyn_poverty_census_tracts', overwrite=True)


Write an existing pandas DataFrame to CARTO.

.. code:: python

    import pandas as pd
    import cartoframes
    df = pd.read_csv('acadia_biodiversity.csv')
    cc = cartoframes.CartoContext(base_url=BASEURL,
                                  api_key=APIKEY)
    cc.write(df, 'acadia_biodiversity')


Map workflow
~~~~~~~~~~~~

The following will embed a CARTO map in a Jupyter notebook, allowing for custom styling of the maps driven by `Turbo Carto <https://github.com/CartoDB/turbo-carto>`__ and `CartoColors <https://carto.com/blog/introducing-cartocolors>`__. See the `CartoColor wiki <https://github.com/CartoDB/CartoColor/wiki/CARTOColor-Scheme-Names>`__ for a full list of available color schemes.

.. code:: python

    from cartoframes import Layer, BaseMap, styling
    cc = cartoframes.CartoContext(base_url=BASEURL,
                                  api_key=APIKEY)
    cc.map(layers=[BaseMap('light'),
                   Layer('acadia_biodiversity',
                         color={'column': 'simpson_index',
                                'scheme': styling.tealRose(5)}),
                   Layer('peregrine_falcon_nest_sites',
                         size='num_eggs',
                         color={'column': 'bird_id',
                                'scheme': styling.vivid(10))],
           interactive=True)


Augment from Data Observatory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Note:** This is a provisional function, so the signature may change.

Interact with CARTO's `Data Observatory <https://carto.com/docs/carto-engine/data>`__:

.. code:: python

    import cartoframes
    cc = cartoframes.CartoContext(BASEURL, APIKEY)

    # total pop, high school diploma (normalized), median income, poverty status (normalized)
    # See Data Observatory catalog for codes: https://cartodb.github.io/bigmetadata/index.html
    data_obs_measures = [{'numer_id': 'us.census.acs.B01003001'},
                         {'numer_id': 'us.census.acs.B15003017',
                          'normalization': 'predenominated'},
                         {'numer_id': 'us.census.acs.B19013001'},
                         {'numer_id': 'us.census.acs.B17001002',
                          'normalization': 'predenominated'},]
    df = cc.data_augment('transactions', data_obs_measures)
    df.head()
