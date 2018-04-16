### Data Observatory

Interact with CARTO’s [Data Observatory](https://carto.com/docs/carto-engine/data):

```python
import cartoframes
cc = cartoframes.CartoContext(BASEURL, APIKEY)

\# total pop, high school diploma (normalized), median income, poverty status (normalized)
\# See Data Observatory catalog for codes: https://cartodb.github.io/bigmetadata/index.html
data\_obs\_measures = \[{'numer_id': 'us.census.acs.B01003001'},
                     {'numer_id': 'us.census.acs.B15003017',
                      'normalization': 'predenominated'},
                     {'numer_id': 'us.census.acs.B19013001'},
                     {'numer_id': 'us.census.acs.B17001002',
                      'normalization': 'predenominated'},\]
df = cc.data('transactions', data\_obs\_measures)
```