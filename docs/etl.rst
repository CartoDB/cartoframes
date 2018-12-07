ETL with cartoframes
====================

One common use case for cartoframes is its use in an ETL (Extract, Transform, and Load) process. The most common pattern is to load the data into CARTO:

.. code::

    from cartoframes import CartoContext
    import pandas as pd

    # create cartocontext for your carto account
    cc = CartoContext(<your credentials>)

    # Extract into a pandas' DataFrame (can be replaced by other operation)
    raw_data = pd.read_csv('https://<remote location>.csv')

    # Transform
    processed_data = <some processing pipeline>

    # Load into your carto account
    cc.write(processed_data, 'processed_data')


Use cases:

- Syncing datasets that aren't accessible to the Import API's sync option or that need intermediate processing
- Connecting datasets that reside in datalakes to CARTO
- Subsampling large datasets for preview in CARTO

Some more examples:

- `Hive -> CARTO connector <https://github.com/andy-esch/hive-carto-connector>`__
- `Accessing and parsing a live data feed <https://city-informatics.com/cartoframes-dashboard-tutorial/>`__
- `Live Power Outage reporting for Massachusetts <https://github.com/jhaddadin/massoutagemap>`__
