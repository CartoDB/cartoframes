## Publishing and Sharing Visualizations

We're going to get through how to publish a visualization by getting the final URL to share it. For that purpose, we'll need to use the "CARTO custom visualizations", as known as **Kuviz**.

Let's start by creating a default context.

```py
from cartoframes.auth import set_default_context

set_default_context('https://your_carto_user.carto.com/')
```

### Publish

#### Case 1: using a synchronized and public table

The 'publish' method uses 'default_public' by default. Therefore, I don't need to use my API Key in this case. Additionally, it's possible to publish a visualization with **password**.

```py
from cartoframes.viz import Map, Layer

tmap = Map(Layer('public_table_name')) # -> Set here a table name from your account
tmap.publish('cf_publish_case_1')
tmap.publish('cf_publish_case_1_password', password="1234")
```

#### Case 2: using a synchronized and private table

In this case it's mandatory to add the `maps_api_key` parameter in the publish method. You can get more info at https://carto.com/developers/auth-api/guides/types-of-API-Keys/. This is due to the `publish` method uses `default_public` by default, and the dataset is private.

```py
from cartoframes.viz import Map, Layer

tmap = Map(Layer('private_table_name')) # -> Set here a table name from your account
tmap.publish('cf_publish_case_2', maps_api_key='your_maps_api_key')
```

#### Case 3: using a non-synchronized and private table

If you try to publish a non synchronized dataset, you will get an **error**:

> 'The map layers are not synchronized with CARTO. Please, use the `sync_data` before publishing the map'

As the error message says, we'll need to make a previous step sychronizing the data. Once it's been syncrhonized, as your new table will be private, you will need to create a Maps API key **with permissions** for your new private table from your CARTO dashboard or Auth API. 

Finally, we will be ready to publish the visualization!

```py
from cartoframes.viz import Map, Layer
from cartoframes.data import Dataset

ds = Dataset.from_table('private_table_name')
ds.download()
ds._is_saved_in_carto = False

tmap = Map(Layer(ds))

tmap.sync_data('private_table_name_sync')
tmap.publish('cf_publish_case_2', maps_api_key='your_maps_api_key')
```

### Update

1. Publish

```py
from cartoframes.viz import Map, Layer

tmap = Map(Layer('public_table_name'))
tmap.publish('cf_publish_update_1')
```

2. Update

```py
from cartoframes.viz import Map, Layer

tmap.update_publication('cf_publish_update_2', password=None)
```

2. Add password

```py
from cartoframes.viz import Map, Layer

tmap.update_publication('cf_publish_update_2', password='1234)
```

### Delete

```py
from cartoframes.viz import Map, Layer

tmap = Map(Layer('public_table_name'))
tmap.publish('cf_publish_delete_1')
tmap.delete_publication()
```

### Get All Visualizations

```py
from cartoframes.viz import Map
Map.all_publications()
```