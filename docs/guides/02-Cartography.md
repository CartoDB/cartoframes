## Cartography

Map creation in cartoframes happens through the `CartoContext.map` method. This method takes a list of map layers, each with independent styling options. The layers can be a base map (`BaseMap`), table layer (`Layer`), or a query against data in the user's CARTO account (`QueryLayer`). Each of the layers is styled independently and appear on the map in the order listed. Basemaps are an exception to this ordering rule: they always appear on the bottom regardless of its order in the list.

### Base Maps

To create a map with only the `BaseMap`, do the following:

```python
from cartoframes import CartoContext, BaseMap
cc = CartoContext(
    base_url='your base url',
    api_key='your api key'
)
cc.map(layers=BaseMap())
```

Or more simply, the last line can be made simpler because a base map is added by default if one is not provided:

```python
cc.map()
```

This produces the following output:

<img src="https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers0_time0_baseid2_labels0_zoom1/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%7D&anti_cache=0.8603790764089185&zoom=1&lat=0&lon=0" />

To get a custom view, pass the longitude, latitude, and zoom as arguments to `cc.map`:

```python
cc.map(lat=34.7982209, lng=113.6489703, zoom=11)
```

To change the base map style to CARTO's 'dark matter', pass `'dark'` to the `BaseMap` class:

```python
cc.map(layers=BaseMap('dark'))
```
<img src="https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers0_time0_baseid1_labels0_zoom1/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%7D&anti_cache=0.8603790764089185&zoom=1&lat=0&lon=0" />

For a light base map, change the source to `'light'`.

<img src="https://cartoframes.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers0_time0_baseid0_labels0_zoom1/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%7D&anti_cache=0.8603790764089185&zoom=1&lat=0&lon=0" />

Remove labels with `labels=None` or put them in back with `labels='back'`.

### Single Layer Map

To add a data layer to your map, first find a table you want to visualize. Here we're going to use

Then use the following code to visualize this data. We're going to use the NYC Taxi dataset from cartoframes examples.

See the [cartoframes Quickstart]({{ site.url }}//documentation/cartoframes/guides/quickstart/).

```python
cc.map(layers=[
    BaseMap(),
    Layer('your table name')
])
```

### Multi-layer Map

To add several layers to your map, add them in the order you want them to display:

```python
cc.map(layers=[
    BaseMap(),
    Layer('biodiversity'),
    QueryLayer("SELECT * FROM table WHERE type != 'bird'")
])
```

### Style Size by Variable

To style by size variable, use the `size` keyword at the layer level for each layer passed. This only work for point data.

This sizes each point the same size (15 pixels wide).

```python
cc.map(layers=Layer('acadia_biodiversity', size=15))
```

To size by a variable, pass a column name instead of a number:

```python
cc.map(
    layers=Layer(
        'acadia_biodiversity',
        size='simpson_index'
    ))
```


### Style Color by Variable

Styling values by color is similar to styling by size but using the `color` keyword in the Layer object instead. Color by value works for points, lines, and polygons.

### Animated Map
