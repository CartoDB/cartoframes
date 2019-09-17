## Sources

In CARTOframes, the `Sources` are the origin of the data. In this guide, we cover the different types of sources that can be used with CARTOframes.

The basic syntax to set the `Source` of a visualization is:

```py
from cartoframes.viz import Map, Layer, Source

Map(Layer(Source('your_source_goes_here')))
```

You don't need to use the `Source` class to create the source for the layer, as it is automatically casted when sent as the first parameter:

```py
from cartoframes.viz import Map, Layer

Map(Layer('your_source_goes_here'))
```

### Table name

Create a new `Source` passing the name of your table in CARTO:

```py
from cartoframes.viz import Map, Layer

Map(Layer('your_table_name'))
```

### SQL Query

```py
from cartoframes.viz import Map, Layer

Map(Layer('SELECT * FROM your_table_name LIMIT 10'))
```

### GeoJSON

```py
from cartoframes.viz import Map, Layer

Map(Layer('your_file_name.geojson'))
```

### DataFrame

```py
from cartoframes.viz import Map, Layer
import pandas as pd

data = {'latitude': [0, 10, 20, 30], 'longitude': [0, 10, 20, 30]}
df = pd.DataFrame.from_dict(data)

Map(Layer(df))
```

### Dataframe from CARTO

```py
from cartoframes.viz import Map, Layer
from cartoframes.data import Dataset

ds = Dataset('your_table_name')

df = ds.download(limit=10)

Map(Layer(df))
```

### Table from CARTO using Dataset

```py
from cartoframes.viz import Map, Layer
from cartoframes.data import Dataset

ds = Dataset('populated_places')

Map(Layer(ds))
```

### Pandas Dataframe

```py
from cartoframes.viz import Map, Layer
import pandas as pd

data = {'latitude': [0, 10, 20, 30], 'longitude': [0, 10, 20, 30]}
df = pd.DataFrame.from_dict(data)
ds = Dataset(df)

Map(Layer(ds))
```
