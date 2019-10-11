## Publishing and Sharing Visualizations

This guide walks through the steps to publish a visualization and get a URL to share it. To do this, we'll need to use "CARTO custom visualizations", also known as **Kuviz**.

Let's start by creating a default credentials. You will need to use your `master API key` in the notebook in order to create a visualization, but it is not going to used in your visualization and your `mater API key` will not be shared:
- The visualizations use `default public API key` when possible (if you use public datasets from your CARTO account).
- If it is not possible, a `regular API key` is created with read only permissions of your data used in the map.

You can get more info about API keys at https://carto.com/developers/auth-api/guides/types-of-API-Keys/

```py
from cartoframes.auth import Credentials, set_default_credentials

set_default_credentials(Credentials.from_file())
```

### Publish

#### Case 1: public dataset from your CARTO account

As you are using a public table from your account, the publish method uses default public API key.

```py
from cartoframes.viz import Map, Layer

public_data_map = Map(Layer('public_table_name')) # -> Set here a public table name from your account
public_data_map.publish('public_data_map')
```

#### Case 2: private dataset from your CARTO account

```py
from cartoframes.viz import Map, Layer

private_data_map = Map(Layer('private_table_name')) # -> Set here a private table name from your account
private_data_map.publish('cf_publish_case_2')
```

#### Case 3: local data

```py
from cartoframes.viz import Map, Layer
from cartoframes.data import Dataset

# getting a DataFrame from a table for the example
# but you can try it with the DataFrame you wish
ds = Dataset('rings') # -> Set here a table name from your account
df = ds.download()

# create the map with your DataFrame
ds = Dataset(df)
local_data_map = Map(Layer(ds))

local_data_map.publish('local_data_map')
```

### Publish with password

In any of the previous cases, you could create the shared visualization with a password. You only need to add a password parameter in the publish method:

```py
from cartoframes.viz import Map, Layer

tmap = Map(Layer('public_table_name'))
public_data_map.publish('public_data_map_with_password', password="1234")
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
