Map Workflows
=============

There are two methods for creating maps in cartoframes: :ref:`maps based on vector
data <vl_anchor>` using the CARTO VL library or :ref:`maps based on raster
data <cartojs_anchor>` by using CARTO's Static Maps API and CARTO.js library.
All maps can be exported as files or displayed interactively in a Jupyter
notebook.

.. _vl_anchor:

Interactive CARTO VL Maps
-------------------------

Interactive `CARTO VL <https://carto.com/developers/carto-vl/>`__ maps are the
recommended way to create maps in cartoframes. These maps have a powerful API
which exposes many features of the CARTO VL mapping library, including
automatic legend generation. With the use of the :py:mod:`helper functions <cartoframes.viz.helpers>`, maps are
created with great cartographic defaults out-of-the-box and include legends and
popups automatically.

.. autoclass:: cartoframes.viz.Map
    :noindex:
    :members:
    :member-order: bysource


Helper Functions
^^^^^^^^^^^^^^^^

.. automodule:: cartoframes.viz.helpers
   :noindex:
   :members:

Vector Layers
^^^^^^^^^^^^^

.. autoclass:: cartoframes.viz.Layer
   :noindex:

.. _cartojs_anchor:

Interactive CARTO.js Maps
-------------------------

CARTOframes also supports interactive and static maps based on raster tiles.
The static outputs are matplotlib axes, so they can be added to subplots to
accompany charts and other maps. The interactive maps are HTML documents that
display in a notebook or can be exported.

.. automethod:: cartoframes.auth.Context.map
    :noindex:

Raster Layers
^^^^^^^^^^^^^

.. autoclass:: cartoframes.layer.BaseMap
    :noindex:

.. autoclass:: cartoframes.layer.Layer
    :inherited-members:
    :noindex:

.. autoclass:: cartoframes.layer.QueryLayer
    :noindex:

