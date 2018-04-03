## Quickstart Guide

### Installing CARTOframes
You can install CARTOframes with PIP. Simply type

```bash
pip install cartoframes
```
This should install install cartoframes to your system, if you want to install it to
a virtual environment you can can run

```bash
virtualenv cartoframes
source env/activate
pip install cartoframes
```


### Installing jupyter notebook

### Starting jupyter notebook

### Authentication
Before we can do anything with CARTOframes we

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
