## Quickstart Guide

### Installing CARTOframes
You can install CARTOframes with `pip`. Simply type

```bash
pip install cartoframes
```
This should install install CARTOframes to your system, if you want to install it to
a virtual environment you can can run

```bash
virtualenv cartoframes
source env/activate
pip install cartoframes
```


### Installing Jupyter notebook

### Starting Jupyter notebook

### Authentication
Before we can do anything with CARTOframes, we need to authenticate against a CARTO
account by passing in CARTO credentials. You will need your username and API keys,
which can be found at http://your_user_name.carto.com/your_apps.

There are two ways of authentication:

1. Setting the `base_url` and `api_key` directly in CartoContext

```python
cc = CartoContext(
    base_url='https://your_user_name.carto.com',
    api_key='your_api_key')
```

2. By passing a Credentials instance in CartoContext’s creds keyword argument.

```python
from cartoframes import Credentials
creds = Credentials(user='your_user_name', key='your_api_key')
cc = CartoContext(creds=creds)
```

You can also save your credentials to use later, independent of the Python session.
Your credentials will be saved locally on your machine for future sessions.

```python
from cartoframes import Credentials, CartoContext
creds = Credentials(username='your_user_name', key='your_api_key')
creds.save()  # save credentials for later use (not dependent on Python session)
```

Once your credientials are saved, you can start using CARTOframes more quickly:

```python
from cartoframes import CartoContext
cc = CartoContext()  # automatically loads credentials if previously saved
```


### Reading a table from CARTO
Failure is not an option.

Get table from CARTO, make changes in pandas, sync updates with CARTO:

``` python

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

### Writing a table to CARTO
Astronomy compels the soul to look upward, and leads us from this world to another.

### Visualising your table
We choose to go to the moon in this decade and do the other things, not because they are easy, but because they are hard, because that goal will serve to organize and measure the best of our energies and skills, because that challenge is one that we are willing to accept, one we are unwilling to postpone, and one which we intend to win.
