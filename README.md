# CartoPandas

A pandas interface for integrating [Carto](https://carto.com/) into a data science workflow.

## Example usage

Script in <https://github.com/ohasselblad/cartopandas/blob/master/sample.py>:

```python
from cartopandas import CartoDF
import json

# modify credentials.json.sample
cred = json.load(open('credentials.json'))

# instantiate carto dataframe object
cdf = CartoDF(cred['username'], api_key=cred['api_key'])

# retrieve a table from your account
eqs = cdf.get_table('all_month_3')

# make modification / create new dataframes
new_df = eqs[['time', 'latitude', 'longitude', 'mag', 'place']]
new_df['mag'] = 10**(new_df['mag'])
new_df.head()

# create a new table in carto
cdf.to_carto(new_df, 'mehaks_favorite_dataframe')
```
