***********
CARTOframes
***********

.. image:: https://travis-ci.org/CartoDB/cartoframes.svg
    :target: https://travis-ci.org/CartoDB/CARTOframes
.. image:: https://img.shields.io/badge/pypi-v1.0b6-orange
    :target: https://pypi.org/project/cartoframes/1.0b6

A Python package for integrating `CARTO <https://carto.com/>`__ maps, analysis, and data services into data science workflows.

Python data analysis workflows often rely on the de facto standards `pandas <http://pandas.pydata.org/>`__ and `Jupyter notebooks <http://jupyter.org/>`__. Integrating CARTO into this workflow saves data scientists time and energy by not having to export datasets as files or retain multiple copies of the data. Instead, CARTOframes give the ability to communicate reproducible analysis while providing the ability to gain from CARTO's services like hosted, dynamic or static maps and `Data Observatory <https://carto.com/platform/location-data-streams/>`__ augmentation.

Try it Out
==========

* Stable (v0.10.1): |stable|
* Beta (v1.0b6): |beta|
* Latest (develop branch): |develop|

.. |stable| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/cartodb/cartoframes/v0.10.1?filepath=examples

.. |beta| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/cartodb/cartoframes/v1.0b6?filepath=examples

.. |develop| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/cartodb/cartoframes/develop?filepath=examples

If you do not have an API key, you can still use cartoframes for creating maps locally.

    The example context only provides read access, so not all cartoframes features are available. For full access, `Start a free 14 day trial <https://carto.com/signup>`__ or get free access with a `GitHub Student Developer Pack <https://education.github.com/pack>`__.

Features
========

- Create interactive maps from pandas DataFrames (CARTO account not required)
- Publish interactive maps to CARTO's platform
- Write and read pandas DataFrames to/from CARTO tables and queries
- Create customizable, interactive CARTO maps in a Jupyter notebook using DataFrames or hosted data
- Augment your data with CARTO's Data Observatory
- Use CARTO for cloud-based analysis

Common Uses
===========

- Visualize spatial data programmatically as matplotlib images, as notebook-embedded interactive maps, or published map visualizations
- Perform cloud-based spatial data processing using CARTO's analysis tools
- Extract, transform, and Load (ETL) data using the Python ecosystem for getting data into and out of CARTO
- Data Services integrations using CARTO's `Location Data Streams <https://carto.com/platform/location-data-streams/>`__

More info
=========

- Complete documentation: https://carto.com/developers/cartoframes/
- Source code: https://github.com/CartoDB/cartoframes
- Bug tracker / feature requests: https://github.com/CartoDB/cartoframes/issues

    `cartoframes` users must have a CARTO API key for most `cartoframes` functionality. For example, writing DataFrames to an account, reading from private tables, and visualizing data on maps all require an API key. CARTO provides API keys for education and nonprofit uses, among others. Request access at support@carto.com. API key access is also given through `GitHub's Student Developer Pack <https://carto.com/blog/carto-is-part-of-the-github-student-pack>`__.

Install Instructions
====================

To install `cartoframes` on your machine, do the following to install the
latest version:

.. code:: bash

    $ pip install cartoframes

To install the 1.0b6 beta version:

.. code:: bash

    $ pip install cartoframes==1.0b6

`cartoframes` is continuously tested on Python versions 2.7, 3.5, 3.6, and 3.7. It is recommended to use `cartoframes` in Jupyter Notebooks (`pip install jupyter`). See the example usage section below or notebooks in the `examples directory <https://github.com/CartoDB/cartoframes/tree/master/examples>`__ for using `cartoframes` in that environment.

Example usage
=============

Data workflow
-------------

Get table from CARTO, make changes in pandas, sync updates with CARTO:

.. code:: python

    from cartoframes import CartoDataFrame
    from cartoframes.auth import set_default_credentials

    # set your credentials
    set_default_credentials(
        username='your_user_name',
        api_key='your API key'
    )

    # read a table from your CARTO account
    cdf = CartoDataFrame.from_carto('brooklyn_poverty_census_tracts')

    # perform operations on you dataframe
    cdf['poverty_per_pop'] = cdf['poverty_count'] / cdf['total_population']

    # update CARTO table with all changes from this session
    cdf.to_carto(
        table_name='brooklyn_poverty_census_tracts',
        if_exists='replace'
    )

Map workflow
------------

Render Interactive Maps
^^^^^^^^^^^^^^^^^^^^^^^

Interactive vector maps can be created programmatically in CARTOframes. In addition to hosted tables and queries, these maps can also display geographic information in pandas DataFrames and geopandas GeoDataFrames. This means that these maps do not need to be tied to a CARTO account (i.e., no need for an API key).

.. code:: python

    from cartoframes.viz import Map
    from cartoframes.viz.helpers import color_continuous_layer
    from cartoframes.auth import set_default_credentials

    set_default_credentials('cartoframes')

    # display map in a notebook
    Map(color_continuous_layer('brooklyn_poverty', 'poverty_per_pop'))

Publish map to CARTO
^^^^^^^^^^^^^^^^^^^^

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

CARTO Credential Management
---------------------------

Typical usage
^^^^^^^^^^^^^

The most common way to input credentials into cartoframes is through the `set_default_credentials` method, as below. Replace `{your_user_name}` with your CARTO username and `{your_api_key}` with your API key, which you can find at ``https://{your_user_name}.carto.com/your_apps``.

.. code:: python

    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        filepath='your_creds_file.json'
    )

    # or

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
    credentials.save('path/file/creds.json')  # save credentials for later use (not dependent on Python session)

Once you save your credentials, you can get started in future sessions more quickly:

.. code:: python

    from cartoframes.auth import Credentials
    credentials = Credentials.from_file('path/file/creds.json')  # automatically loads credentials if previously saved
