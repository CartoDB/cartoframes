## Cartography

Map creation in cartoframes happens through the `CartoContext.map` method. This method takes a list of map layers, each with independt styling options. The layers can be a `BaseMap`, table layer (`Layer`), or a query against data in the user's CARTO account (`QueryLayer`). Each of the layers is styled independently and appear on the map in the order listed. Basemaps are an exception to this ordering rule: they always appear on the bottom regardless of its order in the list.

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

<iframe srcdoc="<!DOCTYPE html>
<html>
  <head>
    <title>Carto</title>
    <meta name='viewport' content='initial-scale=1.0, user-scalable=no' />
    <meta http-equiv='content-type' content='text/html; charset=UTF-8' />
    <link rel='shortcut icon' href='http://cartodb.com/assets/favicon.ico' />

    <style>
     html, body, #map {
       height: 100%;
       padding: 0;
       margin: 0;
     }
     #zoom-center {
       position: absolute;
       right: 0;
       top: 0;
       background-color: rgba(255, 255, 255, 0.7);
       width: 240px;
       z-index: 100;
       padding: 4px;
     }
    </style>

    <link rel='stylesheet' href='https://cartodb-libs.global.ssl.fastly.net/cartodb.js/v3/3.15/themes/css/cartodb.css' />
  </head>
  <body>
    <div id='zoom-center'>
      zoom=<span id='zoom'>4</span>,
      lng=<span id='lon'>No data</span>, lat=<span id='lat'>No data</span>
    </div>
    <div id='map'></div>
    <script src='https://cartodb-libs.global.ssl.fastly.net/cartodb.js/v3/3.15/cartodb.js'></script>

    <script>
     const config  = {&quot;user_name&quot;: &quot;eschbacher&quot;, &quot;maps_api_template&quot;: &quot;https://eschbacher.carto.com&quot;, &quot;sql_api_template&quot;: &quot;https://eschbacher.carto.com&quot;, &quot;tiler_protocol&quot;: &quot;https&quot;, &quot;tiler_domain&quot;: &quot;carto.com&quot;, &quot;tiler_port&quot;: &quot;80&quot;, &quot;type&quot;: &quot;namedmap&quot;, &quot;named_map&quot;: {&quot;name&quot;: &quot;cartoframes_ver20170406_layers0_time0_baseid2_labels0_zoom1&quot;, &quot;params&quot;: {&quot;basemap_url&quot;: &quot;https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}.png&quot;, &quot;zoom&quot;: 1, &quot;lat&quot;: 0, &quot;lng&quot;: 0}}};
     const bounds  = [];
     const options = {&quot;filter&quot;: [&quot;mapnik&quot;, &quot;torque&quot;], &quot;https&quot;: true};

     const adjustLongitude = (lng) => (
       lng - ((Math.ceil((lng + 180) / 360) - 1) * 360)
     );
     const map = L.map('map', {
       zoom: 1,
       center: [0, 0],
     });

     if (L.Browser.retina) {
         var basemap = config.named_map.params.basemap_url.replace('.png', '@2x.png');
     } else {
         var basemap = config.named_map.params.basemap_url;
     }
     L.tileLayer(basemap, {
         attribution: &quot;&copy; <a href=\&quot;http://www.openstreetmap.org/copyright\&quot;>OpenStreetMap</a>&quot;
     }).addTo(map);
     const updateMapInfo = () => {
       $('#zoom').text(map.getZoom());
       $('#lat').text(map.getCenter().lat.toFixed(4));
       $('#lon').text(adjustLongitude(map.getCenter().lng).toFixed(4));
     };

     cartodb.createLayer(map, config, options)
            .addTo(map)
            .done((layer) => {
              if (bounds.length) {
                map.fitBounds(bounds);
              }
              updateMapInfo();
              map.on('move', () => {
                updateMapInfo();
              });
            })
            .error((err) => {
              console.log('ERROR: ', err);
            });
    </script>

  </body>
</html>
" width=800 height=400>  Preview image: <img src="https://eschbacher.carto.com/api/v1/map/static/named/cartoframes_ver20170406_layers0_time0_baseid2_labels0_zoom1/800/400.png?config=%7B%22basemap_url%22%3A+%22https%3A%2F%2F%7Bs%7D.basemaps.cartocdn.com%2Frastertiles%2Fvoyager_labels_under%2F%7Bz%7D%2F%7Bx%7D%2F%7By%7D.png%22%7D&anti_cache=0.8603790764089185&zoom=1&lat=0&lon=0" /></iframe>

To change the basemap style to CARTO's 'dark matter', pass the source keyword:

```python
cc.map(layers=BaseMap(source='dark'))
```

For a light basemap, change source to `'light'`.

Remove labels with `labels=None` or put them in back with `labels='back'`.

### Single Layer Map

To add a data layer to your map, first find a table you want to visualize. Then use the following code to visualize this data:

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
