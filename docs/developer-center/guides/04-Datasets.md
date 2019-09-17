## Datasets

In CARTOframes, the `Dataset` is the generic data class for cartoframes data operations. It is mainly used to work in your Notebook with local data or with data download from your CARTO account and to upload data to your CARTO account. A `Dataset` instance can be created from a dataframe, geodataframe, a table hosted on a CARTO account, an arbitrary query against a CARTO account, or a local or hosted GeoJSON source.

### Table name

Create a new `Source` passing the name of your table in CARTO:

```py
from cartoframes.auth import set_default_credentials
from cartoframes.data import Dataset

set_default_credentials(
    username='your_user_name',
    api_key='your api key'
)

Dataset('your_table_name')
```

### SQL Query

```py
from cartoframes.auth import set_default_credentials
from cartoframes.data import Dataset

set_default_credentials(
    username='your_user_name',
    api_key='your api key'
)

Dataset('SELECT * FROM your_table_name LIMIT 10')
```

### GeoJSON

```py
from cartoframes.data import Dataset

Dataset('your_file_name.geojson')
```

### DataFrame

```py
from cartoframes.data import Dataset
import pandas as pd

data = {'latitude': [0, 10, 20, 30], 'longitude': [0, 10, 20, 30]}
df = pd.DataFrame.from_dict(data)

Dataset(df)
```

### GeoDataFrame

```py
from cartoframes.data import Dataset
import geopandas

gdf = geopandas.DataFrame(...)

Dataset(gdf)
```

### Download data from CARTO

```py
from cartoframes.auth import set_default_credentials
from cartoframes.data import Dataset

set_default_credentials(
    username='your_user_name',
    api_key='your api key'
)

ds = Dataset('your_table_name')

df = ds.download()
```

### Upload data to CARTO
```py
from cartoframes.auth import set_default_credentials
from cartoframes.data import Dataset
import pandas as pd

set_default_credentials(
    username='your_user_name',
    api_key='your api key'
)

data = {'latitude': [0, 10, 20, 30], 'longitude': [0, 10, 20, 30]}
df = pd.DataFrame.from_dict(data)
ds = Dataset(df)

ds.upload(table_name='your_new_table_name')
```
