API Reference
=============

Introduction
------------

The CARTOframes API is organized in three parts: `auth`, `data`, and `viz`.

`Authentication <#auth>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to use CARTOframes without having a CARTO account. However, to have access to data enritchment or to discover
useful datasets, being a CARTO user offers many advantages.
This module is the responsible for connecting the user with its CARTO account through given user credentials.

`Data Management <#data>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^

From discovering and enritching data to applying data analyisis and geocoding methods, 
CARTOframes API is built with the purpose of managing data without leaving the context of your notebook.

`Data Visualization <#viz>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The viz API is designed to create useful, beautiful and straight forward visualizations.
It is at the same time predefined and flexible, in order to give advanced users the possibility of building specific visualizations, 
but also to offer multiple built-in methods to work faster with a few lines of code.

Auth
----

.. automodule:: cartoframes.auth
    :members:

Data Management
---------------

.. automodule:: cartoframes.data
    :members:

Data Observatory
----------------

  .. automodule:: cartoframes.data.observatory
    :members:


Data Services
-------------

Geocode
^^^^^^^

.. include:: geocode.rst

.. automodule:: cartoframes.data.services
    :members:

Viz
---

.. automodule:: cartoframes.viz
    :members:

Widgets
^^^^^^^

.. automodule:: cartoframes.viz.widgets
    :members:

Helpers
^^^^^^^

.. automodule:: cartoframes.viz.helpers
    :members: