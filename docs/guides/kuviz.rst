Publishing and sharing a map
============================

 .. warning:: Non-public API. It may change with no previous notice

In CARTOframes, you can publish a map visualization and then share it. When you publish the map visualization, you receive an URL where to see your visualization outside of the Notebook, so you can share it or use it where you want.

You will need to use your `master API key` in the notebook in order to create a visualization, but it is not going to used in your visualization and your `mater API key` will not be shared:
- The visualizations use `default public API key` when possible (if you use public datasets from your CARTO account).
- If it is not possible, a `regular API key` is created with read only permissions of your data used in the map.


Publishing a map
----------------

.. code::

    from cartoframes.viz import Map, Layer

    tmap = Map(Layer(PUBLIC_TABLE))
    tmap.publish('cf_publish_case_1')


As you are using a public table from your account, the publish method uses default public API key.

.. code::

    from cartoframes.viz import Map, Layer

    tmap = Map(Layer(PRIVATE_TABLE))
    tmap.publish('cf_publish_case_2')


In this case, a regular API key has been created with read only permissions of your private table.

.. code::
    df = pd.DataFrame(...)
    ds = Dataset(df)
    local_data_map = Map(Layer(ds))
    local_data_map.publish('local_data_map')

In this case, a table has been created in your CARTO account and a `regular API key` with read only permissions of the table.

Anyway, you can publish a map visualization protected by password:

.. code::

    from cartoframes.viz import Map, Layer

    tmap = Map(Layer(PUBLIC_TABLE))
    tmap.publish('cf_publish_case_1_password', password="1234")


In every case, the `publish` method will return the `id`, `url`, `name` and `privacy` of the visualization.



Updating a published visualization
----------------------------------

If you have modified your map after publishing the visualization:


.. code::

    tmap.update_publication('cf_publish_update_1', password=None)


You will have to add the `password` parameter to set again if you want the visualization protected by password or not.


Deleting a published visualization
----------------------------------

.. code::

    tmap.delete_publication()
