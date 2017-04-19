CARTOFrames
===========

A pandas interface for integrating `CARTO <https://carto.com/>`__ into data science workflows.

Python data analysis workflows often rely on the de facto standards `pandas <http://pandas.pydata.org/>`__ and `Jupyter notebooks <http://jupyter.org/>`__. Integrating CARTO into this workflow saves data scientists time and energy by not having to export datasets as files or retain multiple copies of the data. Instead, CARTOFrames give the ability to communicate reproducible analysis while providing the ability to gain from CARTO's services like hosted, dynamic or static maps and `Data Observatory <https://carto.com/data-observatory/>`__ augmentation.

Install Instructions
--------------------

`cartoframes` relies on `pandas <http://pandas.pydata.org/>`__ and a development version of the CARTO Python SDK (on branch `1.0.0 <https://github.com/CartoDB/carto-python/tree/1.0.0>`__). To install `cartoframes` on your machine, do the following:

.. code:: bash

    $ git clone https://github.com/CartoDB/cartoframes.git
    $ cd cartoframes
    $ pip install -r requirements.txt
    $ pip install -e .

Once you've done this, `cartoframes` will be installed. See the example usage section below for using cartoframes in a Jupyter notebook.

**Note:** Eventually `cartoframes` will be fully installable from `pip`.


Example usage
-------------

Data workflow
~~~~~~~~~~~~~

Get table from carto, make changes in pandas, sync updates with carto:

.. code:: python

    import cartoframes
    cc = cartoframes.CartoContext('https://eschbacher.carto.com/', APIKEY)
    df = cc.read('brooklyn_poverty_census_tracts')
    # do fancy pandas operations (add/drop columns, change values, etc.)
    df['poverty_per_pop'] = df['poverty_count'] / df['total_population']

    # updates carto table with all changes from this session
    cc.write(df, 'brooklyn_poverty_census_tracts', overwrite=True)


Associate an existing pandas dataframe with CARTO.

.. code:: python

    import pandas as pd
    import cartoframes
    df = pd.read_csv('acadia_biodiversity.csv')
    cc = cartoframes.CartoContext(BASEURL, APIKEY)
    cc.write(df, 'acadia_biodiversity')


Map workflow
~~~~~~~~~~~~

The following will embed a CARTO map in a Jupyter notebook, allowing for custom styling of the maps driving by `Turbo Carto <https://github.com/CartoDB/turbo-carto>`__ and `CartoColors <https://carto.com/blog/introducing-cartocolors>`__. See the `CartoColor wiki <https://github.com/CartoDB/CartoColor/wiki/CARTOColor-Scheme-Names>`__ for a full list of available color schemes.

.. code:: python

    from cartoframes import Layer, BaseMap
    cc = cartoframes.CartoContext(BASEURL, APIKEY)
    cc.map(layers=[BaseMap(),
                   Layer('acadia_biodiversity',
                         color={'column': 'simpson_index',
                                'scheme': 'TealRose'}),
                   Layer('peregrine_falcon_nest_sites',
                         size='num_eggs',
                         color={'column': 'bird_id',
                                'scheme': 'Vivid')],
           interactive=True)


Augment from Data Observatory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Note: This feature is not yet implemented**

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
