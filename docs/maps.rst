Map Workflows
=============

With CARTOframes you can create :ref:`maps based on vector
data <vl_anchor>` using the CARTO VL library. All maps can be exported as
files or displayed interactively in a Jupyter notebook.

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
