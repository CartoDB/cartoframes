Publishing and sharing a map
============================

 .. warning:: Non-public API. It may change with no previous notice

In CARTOframes, you can publish a map visualization and then share it. When you publish the map visualization, you receive an URL where to see your visualization outside of the Notebook, so you can share it or use it where you want.


Publishing a map
----------------

.. code::

    from cartoframes.viz import Map, Layer, basemaps

    tmap = Map(Layer(PUBLIC_TABLE))
    tmap.publish('cf_publish_case_1')


The 'publish' method uses 'default_public' API key by default. So, if you want to publish a map using private datasets, you should add a Regular API key with permissions to Maps API and the datasets.

.. code::

    from cartoframes.viz import Map, Layer, basemaps

    tmap = Map(Layer(PRIVATE_TABLE))
    tmap.publish('cf_publish_case_2', maps_api_key='YOUR MAPS API KEY')


Anyway, you can publish a map visualization protected by password:

.. code::

    from cartoframes.viz import Map, Layer, basemaps

    tmap = Map(Layer(PUBLIC_TABLE))
    tmap.publish('cf_publish_case_1_password', password="1234")


In every case, the `publish` method will return the `id`, `url`, `name` and `privacy` of the visualization.


Synchrorize data
----------------

If the data used by your map is not synchronized with CARTO, you will need to use `sync_data` method before publishing:

.. code::

    tmap_with_local_data.sync_data(table_name)


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
