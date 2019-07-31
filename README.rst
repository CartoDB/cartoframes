***********
CARTOframes
***********

.. image:: https://travis-ci.org/CartoDB/cartoframes.svg?branch=master
    :target: https://travis-ci.org/CartoDB/cartoframes
.. image:: https://coveralls.io/repos/github/CartoDB/cartoframes/badge.svg?branch=master
    :target: https://coveralls.io/github/CartoDB/cartoframes?branch=master

A Python package for integrating `CARTO <https://carto.com/>`__ maps, analysis, and data services into data science workflows.

Python data analysis workflows often rely on the de facto standards `pandas <http://pandas.pydata.org/>`__ and `Jupyter notebooks <http://jupyter.org/>`__. Integrating CARTO into this workflow saves data scientists time and energy by not having to export datasets as files or retain multiple copies of the data. Instead, CARTOframes give the ability to communicate reproducible analysis while providing the ability to gain from CARTO's services like hosted, dynamic or static maps and `Data Observatory <https://carto.com/platform/location-data-streams/>`__ augmentation.

Try it Out
==========

* Stable (v0.10.1): |stable|
* Latest (develop branch): |develop|

.. |stable| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/cartodb/cartoframes/v0.10.1?filepath=examples

.. |develop| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/cartodb/cartoframes/develop?filepath=examples

Features
========

- Create interactive maps from pandas DataFrames (CARTO account not required)
- Publish interactive maps to CARTO's platform
- Write and read pandas DataFrames to/from CARTO tables and queries
- Create customizable, interactive CARTO maps in a Jupyter notebook using DataFrames or hosted data
- Augment your data with CARTO's Data Observatory
- Use CARTO for cloud-based analysis
- Try it out without needing a CARTO account by using the `Examples functionality <https://cartoframes.readthedocs.io/en/latest/example_context.html>`__

Common Uses
===========

- Visualize spatial data programmatically as matplotlib images, as notebook-embedded interactive maps, or published map visualizations
- Perform cloud-based spatial data processing using CARTO's analysis tools
- Extract, transform, and Load (ETL) data using the Python ecosystem for getting data into and out of CARTO
- Data Services integrations using CARTO's `Location Data Streams <https://carto.com/platform/location-data-streams/>`__

Try it out
==========

The easiest way to try out cartoframes is to use the cartoframes example notebooks running in binder: https://mybinder.org/v2/gh/CartoDB/cartoframes/v0.10.1?filepath=examples If you already have an API key, you can follow along and complete all of the example notebooks.

If you do not have an API key, you can still use cartoframes for creating maps locally.

.. note::
    The example context only provides read access, so not all cartoframes features are available. For full access, `Start a free 14 day trial <https://carto.com/signup>`__ or get free access with a `GitHub Student Developer Pack <https://education.github.com/pack>`__.

More info
=========

- Complete documentation: http://cartoframes.readthedocs.io/en/latest/
- Source code: https://github.com/CartoDB/cartoframes
- bug tracker / feature requests: https://github.com/CartoDB/cartoframes/issues

.. note::
    `cartoframes` users must have a CARTO API key for most `cartoframes` functionality. For example, writing DataFrames to an account, reading from private tables, and visualizing data on maps all require an API key. CARTO provides API keys for education and nonprofit uses, among others. Request access at support@carto.com. API key access is also given through `GitHub's Student Developer Pack <https://carto.com/blog/carto-is-part-of-the-github-student-pack>`__.

Install Instructions
====================

To install `cartoframes` on your machine, do the following to install the
latest version:

.. code:: bash

    $ pip install cartoframes

To install the 1.0b2 beta version:

.. code:: bash

    $ pip install cartoframes==1.0b2

`cartoframes` is continuously tested on Python versions 2.7, 3.5, and 3.6. It is recommended to use `cartoframes` in Jupyter Notebooks (`pip install jupyter`). See the example usage section below or notebooks in the `examples directory <https://github.com/CartoDB/cartoframes/tree/master/examples>`__ for using `cartoframes` in that environment.

Virtual Environment
-------------------

Using `virtualenv`
^^^^^^^^^^^^^^^^^^


Make sure your `virtualenv` package is installed and up-to-date. See the `official Python packaging page <https://packaging.python.org/guides/installing-using-pip-and-virtualenv/>`__ for more information.

To setup `cartoframes` and `Jupyter` in a `virtual environment <http://python-guide.readthedocs.io/en/latest/dev/virtualenvs/>`__:

.. code:: bash

    $ virtualenv venv
    $ source venv/bin/activate
    (venv) $ pip install cartoframes jupyter
    (venv) $ jupyter notebook

To install the 1.0b2 version, run instead:

.. code:: bash

    (venv) $ pip install cartoframes==1.0b2 jupyter

Then create a new notebook and try the example code snippets below with tables that are in your CARTO account.

Using `pipenv`
^^^^^^^^^^^^^^

Alternatively, `pipenv <https://pipenv.readthedocs.io/en/latest/>`__ provides an easy way to manage virtual environments. The steps below are:

1. Create a virtual environment with Python 3.4+ (recommended instead of Python 2.7)
2. Install cartoframes and Jupyter (optional) into the virtual environment
3. Enter the virtual environment
4. Launch a Jupyter notebook server

.. code:: bash

    $ pipenv --three
    $ pipenv install cartoframes jupyter
    $ pipenv run jupyter notebook

To install the 1.0b2 version, run instead:

.. code:: bash

    $ pipenv --three
    $ pipenv install cartoframes==1.0b2 jupyter
    $ pipenv run jupyter notebook

Native pip
----------

If you install packages at a system level, you can install `cartoframes` with:

.. code:: bash

    $ pip install cartoframes

or to install the 1.0b2 version:

.. code:: bash

    $ pip install cartoframes==1.0b2

Example usage
=============

Data workflow
-------------

Get table from CARTO, make changes in pandas, sync updates with CARTO:

.. code:: python

    from cartoframes.auth import set_default_credentials
    from cartoframes.data import Dataset

    # `base_url`s are of the form `https://username.carto.com/` for most users
    set_default_credentials(
        base_url='https://your_user_name.carto.com/',
        api_key='your API key'
    )

    # create a dataset object
    d = Dataset('brooklyn_poverty_census_tracts')

    # read a table from your CARTO account to a DataFrame
    df = d.download()

    # perform operations on you dataframe
    df['poverty_per_pop'] = df['poverty_count'] / df['total_population']

    # update CARTO table with all changes from this session
    d_updated = Dataset(df)
    d_updated.upload(
        table_name='brooklyn_poverty_census_tracts',
        if_exists='replace'
    )

.. image:: https://raw.githubusercontent.com/CartoDB/cartoframes/master/docs/img/data-workflow.gif


Map workflow
------------

There are two types of maps in CARTOframes: vector using `CARTO VL <https://carto.com/developers/carto-vl/>`__ and raster using `CARTO.js <https://carto.com/developers/carto-js/>`__. Vector maps are currently available as interactive HTML documents which can be displayed in a notebook, exported to an HTML file, or published to CARTO's platform. The raster-based maps can be displayed interactively in a notebook or as static matplotlib images.

CARTO VL-based Maps
^^^^^^^^^^^^^^^^^^^

Interactive vector maps can be created programmatically in CARTOframes. In addition to hosted tables and queries, these maps can also display geographic information in pandas DataFrames and geopandas GeoDataFrames. This means that these maps do not need to be tied to a CARTO account (i.e., no need for an API key).

.. code:: python

    from cartoframes.viz import Map
    from cartoframes.viz.helpers import color_continuous_layer
    from cartoframes.auth import set_default_credentials

    set_default_credentials('https://cartoframes.carto.com')

    # display map in a notebook
    Map(color_continuous_layer('brooklyn_poverty', 'poverty_per_pop'))

Publish map to CARTO

.. code:: python

    from cartoframes.viz import Map
    from cartoframes.viz.helpers import color_continuous_layer
    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        base_url='https://your_user_name.carto.com',
        api_key='your api key'
    )

    # display map in a notebook
    bk_map = Map(color_continuous_layer('brooklyn_poverty', 'poverty_per_pop'))
    bk_map.publish('Brooklyn Poverty')

This will publish a map like `this one <https://cartoframes.carto.com/kuviz/2a7badc3-00b3-49d0-9bc8-3b138542cdcf>`__.

Data Observatory
----------------

Interact with CARTO's `Data Observatory <https://carto.com/docs/carto-engine/data>`__:

Example: Get census tracts around Idaho Falls, Idaho, USA, and add median income from the US census. Without limiting the metadata, we get median income measures for each census in the Data Observatory.

.. code:: python

    from cartoframes.auth import set_default_credentials
    from cartoframes.client import DataObsClient

    set_default_credentials(
        base_url='https://your_user_name.carto.com',
        api_key='your api key'
    )

    do = DataObsClient()

    # will return Dataset with columns `the_geom` and `geom_ref`
    tracts = do.boundaries(
        boundary='us.census.tiger.census_tract',
        region=[-112.096642,43.429932,-111.974213,43.553539])

    # write geometries to a CARTO table
    tracts.upload('idaho_falls_tracts')

    # gather metadata needed to look up median income
    median_income_meta = do.discovery(
        'idaho_falls_tracts',
        keywords='median income',
        boundaries='us.census.tiger.census_tract')

    # get median income data and original table as new Dataset
    idaho_falls_income = do.augment(
        'idaho_falls_tracts',
        median_income_meta,
        how='geom_refs')

    # overwrite existing table with newly-enriched Dataset
    idaho_falls_income.upload('idaho_falls_tracts', if_exists='replace')


CARTO Credential Management
---------------------------

Typical usage
^^^^^^^^^^^^^

The most common way to input credentials into cartoframes is through the `set_default_credentials` method, as below. Replace `{your_user_name}` with your CARTO username and `{your_api_key}` with your API key, which you can find at ``https://{your_user_name}.carto.com/your_apps``.

.. code:: python

    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='{your_user_name}',
        api_key='{your_api_key}'
    )

When the data we’re going to use is public, we don’t need the api_key parameter, it’s automatically set to default_public:

.. code:: python

    from cartoframes.auth import set_default_credentials

    set_default_credentials('your_user_name')

You can also set your credentials using the `base_url` parameter:

.. code:: python

    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        base_url='https://{your_user_name}.carto.com',
        api_key='{your_api_key}'
    )


Save/update credentials for later use
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from cartoframes.auth import Credentials

    credentials = Credentials('{your_user_name}', '{your_api_key}')
    credentials.save()  # save credentials for later use (not dependent on Python session)

Once you save your credentials, you can get started in future sessions more quickly:

.. code:: python

    from cartoframes.auth import Credentials
    credentials = Credentials.from_file()  # automatically loads credentials if previously saved
