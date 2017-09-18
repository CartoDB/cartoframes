===========
CARTOFrames
===========

.. image:: https://travis-ci.org/CartoDB/cartoframes.svg?branch=master
    :target: https://travis-ci.org/CartoDB/cartoframes
.. image:: https://coveralls.io/repos/github/CartoDB/cartoframes/badge.svg?branch=master
    :target: https://coveralls.io/github/CartoDB/cartoframes?branch=master

A Python package for integrating `CARTO <https://carto.com/>`__ maps, analysis, and data services into data science workflows.

Python data analysis workflows often rely on the de facto standards `pandas <http://pandas.pydata.org/>`__ and `Jupyter notebooks <http://jupyter.org/>`__. Integrating CARTO into this workflow saves data scientists time and energy by not having to export datasets as files or retain multiple copies of the data. Instead, CARTOFrames give the ability to communicate reproducible analysis while providing the ability to gain from CARTO's services like hosted, dynamic or static maps and `Data Observatory <https://carto.com/data-observatory/>`__ augmentation.

Features

- Write pandas DataFrames to CARTO tables
- Read CARTO tables and queries into pandas DataFrames
- Create customizable, interactive CARTO maps in a Jupyter notebook
- Interact with CARTO's Data Observatory
- Use CARTO's spatially-enabled database for analysis

More info

- Complete documentation: https://cartodb.github.io/cartoframes
- Source code: https://github.com/CartoDB/cartoframes
- bug tracker / feature requests: https://github.com/CartoDB/cartoframes/issues

.. note::
    `cartoframes` users must have a CARTO API key for most `cartoframes` functionality. For example, writing DataFrames to an account, reading from private tables, and visualizing data on maps all require an API key. CARTO provides API keys for education and nonprofit uses, among others. Request access at support@carto.com. API key access is also given through `GitHub's Student Developer Pack <https://carto.com/blog/carto-is-part-of-the-github-student-pack>`__.

Install Instructions
====================

To install `cartoframes` (currently in beta) on your machine, do the following to install the latest pre-release version:

.. code:: bash

    $ pip install --pre cartoframes

It is recommended to use `cartoframes` in Jupyter Notebooks (`pip install jupyter`). See the example usage section below or notebooks in the `examples directory <https://github.com/CartoDB/cartoframes/tree/master/examples>`__ for using `cartoframes` in that environment.

Virtual Environment
-------------------

To setup `cartoframes` and `Jupyter` in a `virtual environment <http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/#basic-usage>`__:

.. code:: bash

    $ virtualenv venv
    $ source venv/bin/activate
    (venv) $ pip install --pre cartoframes
    (venv) $ pip install jupyter
    (venv) $ jupyter notebook

Then create a new notebook and try the example code snippets below with tables that are in your CARTO account.

Example usage
=============

Data workflow
-------------

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
------------

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
-----------------------------

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


CARTO Credential Management
---------------------------

Save and update your CARTO credentials for later use.

.. code:: python

    from cartoframes import Credentials, CartoContext
    creds = Credentials(username='eschbacher', key='abcdefg')
    creds.save()  # save credentials for later use (not dependent on Python session)

Once you save your credentials, you can get started in future sessions more quickly:

.. code:: python

    from cartoframes import CartoContext
    cc = CartoContext()  # automatically loads credentials if previously saved
