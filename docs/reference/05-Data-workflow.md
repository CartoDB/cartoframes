### Data workflow

Get table from CARTO, make changes in pandas, sync updates with CARTO:

```python
import cartoframes
# `base_url`s are of the form `http://{username}.carto.com/` for most users
cc = cartoframes.CartoContext(base_url='https://eschbacher.carto.com/',
                              api_key=APIKEY)

# read a table from your CARTO account to a DataFrame
df = cc.read('brooklyn_poverty_census_tracts')

# do fancy pandas operations (add/drop columns, change values, etc.)
df['poverty_per_pop'] = df['poverty_count'] / df['total_population']

# updates CARTO table with all changes from this session
cc.write(df, 'brooklyn_poverty_census_tracts', overwrite=True)
```

![../../img/read_demo.gif](../../img/read_demo.gif)

Write an existing pandas DataFrame to CARTO.

```python
import pandas as pd
import cartoframes
df = pd.read_csv('acadia_biodiversity.csv')
cc = cartoframes.CartoContext(base_url=BASEURL,
                              api_key=APIKEY)
cc.write(df, 'acadia_biodiversity')
```
