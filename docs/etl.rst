ETL with cartoframes
====================

One common use case for cartoframes is its use in an ETL (Extract, Transform, and Load) process. The most common pattern is to load the data into CARTO:

.. code::

    from cartoframes.auth import Context
    from cartoframes.data import Dataset
    import pandas as pd

    # create cartocontext for your carto account
    cc = Context(<your credentials>)

    # Extract into a pandas' DataFrame (can be replaced by other operation)
    raw_data = pd.read_csv('https://<remote location>.csv')

    # Transform
    processed_data = <some processing pipeline>

    # Load into your carto account
    cc.write(processed_data, 'processed_data')


Read data from PostgreSQL to CARTO
----------------------------------

.. code::

    from cartoframes.auth import Context
    from cartoframes.data import Dataset

    import pandas as pd
    import sqlalchemy as sqla

    connection_string = 'postgresql://localhost:5432'  # replace with your connection string
    engine = sql.create_engine(connect_string)
    raw_data = pd.read_sql_query('arbitrary sql query', con=engine)

    # do something with this data
    # for example, create a map from the dataframe with lat/lng columns
    Map(Layer(raw_data))

    # send to carto
    pg_dataset = Dataset.from_dataframe(df)
    pg_dataset.upload(table_name='table_from_pg_db')


Use cases
---------

- Syncing datasets that aren't accessible to the Import API's sync option or that need intermediate processing
- Connecting datasets that reside in datalakes to CARTO
- Subsampling large datasets for preview in CARTO

Examples
--------

- `Hive -> CARTO connector <https://github.com/andy-esch/hive-carto-connector>`__
- `Accessing and parsing a live data feed <https://city-informatics.com/cartoframes-dashboard-tutorial/>`__
- `Live Power Outage reporting for Massachusetts <https://github.com/jhaddadin/massoutagemap>`__
