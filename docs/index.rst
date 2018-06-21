.. cartoframes documentation master file, created by
   sphinx-quickstart on Mon Feb 27 17:03:44 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../README.rst

.. toctree::
   :maxdepth: 2

*************************
CARTOframes Functionality
*************************

CartoContext
============
.. autoclass:: cartoframes.context.CartoContext
    :noindex:
    :member-order: bysource
    :members: read, query, delete, map, data_discovery, data, data_boundaries, tables

    .. automethod:: write(df, table_name, temp_dir=SYSTEM_TMP_PATH, overwrite=False, lnglat=None, encode_geom=False, geom_col=None, \*\*kwargs)

Map Layer Classes
=================
.. autoclass:: cartoframes.layer.BaseMap
    :noindex:

.. autoclass:: cartoframes.layer.Layer
    :inherited-members:
    :noindex:

.. autoclass:: cartoframes.layer.QueryLayer
    :noindex:

Map Styling Functions
=====================
.. automodule:: cartoframes.styling
    :noindex:
    :members:
    :member-order: bysource

BatchJobStatus
==============
.. autoclass:: cartoframes.context.BatchJobStatus
    :noindex:
    :members:

Credentials Management
======================
.. automodule:: cartoframes.credentials
    :noindex:
    :members:

Example Datasets
================
.. automodule:: cartoframes.examples

Data access functions
---------------------
.. autofunction:: cartoframes.examples.read_brooklyn_poverty
.. autofunction:: cartoframes.examples.read_mcdonalds_nyc
.. autofunction:: cartoframes.examples.read_nat
.. autofunction:: cartoframes.examples.read_nyc_census_tracts
.. autofunction:: cartoframes.examples.read_taxi

Example CartoContext
--------------------

.. autoclass:: cartoframes.examples.Examples
    :members: read_brooklyn_poverty, read_mcdonalds_nyc, read_nat, read_nyc_census_tracts, read_taxi

contrib
=======

contrib is an experimental library of modules in the `contrib` directory. These modules allow us to release new features with the expectation that they will change quickly, but give users quicker access to the bleeding edge. Most features in `contrib` will eventually be merged into the cartoframes core.

vector maps
-----------
.. automodule:: cartoframes.contrib.vector
    :members:


******************
Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

*******
Version
*******

:Version: |version|
