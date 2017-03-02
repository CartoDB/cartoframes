CartoFrames
===========

A pandas interface for integrating `Carto <https://carto.com/>`__ into a
data science workflow.

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

.. figure:: examples/read_carto.png
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

.. figure:: examples/carto_map.png
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
    df.head(10)

.. figure:: examples/data_obs_augmentation.png
   :alt: Example of using data observatory augmentation methods

