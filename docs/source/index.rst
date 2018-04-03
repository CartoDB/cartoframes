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
    :members: read, query, delete, map, data_discovery, data, data_boundaries

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

******************
Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

:Version: |version|
