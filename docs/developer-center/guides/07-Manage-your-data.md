## Manage your data

This guide provides the necessary information to upload, download and work with data both locally and with the CARTO platform.
The first thing that should be taken into account is the fact that having a CARTO account is not needed to manipulate data. With CARTOframes, anyone can use local or external data.

### Downloading external data with Pandas

When looking for data, each platform or service uses different file formats. There are multiple formats out there: CSV, GeoJSON, JSON, XML, Shapefile, etc. This guide illustrates how to use the [Pandas Data Analysis Library](https://pandas.pydata.org/) to download and parse data. 

Many platforms offer the possibility of exporting data. Therefore, one option is to export the desired data into a file and read the content with pandas. In the following example, pandas method `read_csv` returns a [DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) object.

```python
df = pandas.read_csv('my_exported_file.csv')
df.head()
```

However, with Pandas it is also possible to read **remote** data. For instance, the [Paris Open Data Portal](https://opendata.paris.fr) exposes data in **endpoints** that can be reached directly through Pandas, which avoids the previous step of saving the data into a file, but this also requires Internet connection to work since it is necessary to access their site:

```python
df = pandas.read_csv('https://opendata.paris.fr/explore/dataset/sites-disposant-du-service-paris-wi-fi/download/?format=csv')
df.head()
```

Once the **DataFrame** (`df`) has been created, it can be used to create a `Dataset` instance:


```python
from cartoframes.data import Dataset

df = pandas.read_csv('my_exported_file.csv')
ds = Dataset(df)
```

### Uploading a local Dataset to CARTO

There are three things to take into account when uploading a Dataset to CARTO. Having this setup code:

```python
from cartoframes.data import Dataset
from cartoframes.auth import set_default_credentials

set_default_credentials('johnsmith', 'a1b2c3d4e5f6g7h8i9j0k')

df = pandas.read_csv('my_exported_file.csv')
ds = Dataset(df)
ds.upload('my_table_name')
```

1. `if_exists` options

The Dataset must have a table name. However, if the table name already exists in the CARTO account where the dataset is about to be uploaded, it will fail.

```
ds.upload('my_table_name', if_exists=Dataset.IF_EXISTS_REPLACE)
```

2. Coordinates

CARTO needs to know wich fields are the ones that contain the coordinates of each row. This is done through the `with_lnglat` parameter.

```
ds.upload('my_table_name', with_lnglat=('longitude', 'latitude'))
```

3. Updating Dataset info.

To upload a Dataset it is mandatory to use a Master API Key. Therefore, the Dataset will be **private** when created. This can be changed through the `update_dataset_info` method:

```python
ds.update_dataset_info(privacy=Dataset.PRIVACY_PUBLIC)
```

The table name used for this Dataset can also be changed through this method:

```python
ds.update_dataset_info(table_name='another_table_name')
```

### Downloading a Dataset from CARTO

### Modifying the data through a SQL query

### Deleting a Dataset