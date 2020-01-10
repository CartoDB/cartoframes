# RC1 Migration

Migration notes from `1.0b7` to `rc1`

* [Data](#Data)
* [Style](#Style)
* [Popups](#Popups)
* [Widgets](#Widgets)
* [Legends](#Legends)

## Data

<details><summary>Geometry management</summary>
<p>

* From:

```python
from cartoframes import CartoDataFrame

cdf = CartoDataFrame(df, geometry='the_geom')
```

* To:

```python
from geopandas import GeoDataFrame
from cartoframes.utils import decode_geometry

gdf = GeoDataFrame(df, geometry=decode_geometry(df['the_geom']))
```

* From:

```python
from cartoframes import CartoDataFrame

cdf = CartoDataFrame(df)
cdf.set_geometry_from_xy('lng', 'lat', inplace=True)
```

* To:

```python
from geopandas import GeoDataFrame, points_from_xy

gdf = GeoDataFrame(df, geometry=points_from_xy(df['lng'], df['lat']))
```

</p>
</details>

<details><summary>Load data from CARTO</summary>
<p>

* From:

```python
from cartoframes import CartoDataFrame

cdf = CartoDataFrame.from_carto('global_power_plants', limit=100)
```

* To (as we already could):

```python
from cartoframes import read_carto

gdf = read_carto('global_power_plants', limit=100)
```

</p>
</details>

<details><summary>Upload data to CARTO</summary>
<p>

* From:

```python
cdf.to_carto(
    table_name='global_power_plants',
    if_exists='replace'
)
```

* To (as we already could):

```python
from cartoframes import to_carto

to_carto(
    gdf,
    table_name='global_power_plants',
    if_exists='replace'
)
```

</p>
</details>

<details><summary>Visualization</summary>
<p>

* From:

```python
cdf.viz()
```

* To (as we already could):

```python
from cartoframes.viz import Map, Layer

Map(Layer(gdf))

# or Layer(gdf)
```

</p>
</details>

## Style

<details><summary>Use basic_style over "string syntax"</summary>
<p>

Replace CARTO VL style syntax by using style helpers.

* From:

```python
from cartoframes.viz import Map, Layer, Style

Map(
  Layer(
    'table_name',
    style='color: blue strokeColor: white'
  )
)
```

* To:

```python
from cartoframes.viz import Map, Layer, basic_style

Map(
  Layer(
    'table_name',
    style=basic_style(color='blue', stroke_color='white')
  )
)
```

</p>
</details>

<details><summary>Replace layer helpers with style helpers</summary>
<p>

* From:

```python
from cartoframes.viz.helpers import size_category_layer

size_category_layer(
  'roads',
  'type',
  title='Roads sized by category'
)
```

* To:

```python
from cartoframes.viz import Layer, size_category_style

Layer(
  'roads',
  size_category_style('type'),
  title='Roads sized by category'
)
```

</p>
</details>

<details><summary>Layer Helpers</summary>
<p>

Layer helpers have been replaced by style helpers. Now every layer is made by using the Layer class.

* From:

```python
from cartoframes.viz.helpers import color_category_layer

color_category_layer('table', 'column', palette='sunset', legends=False, widgets=True, popups=True, title='Title')
```

* To:

```python
from cartoframes.viz.helpers import Layer, color_category_style

Layer(
    'table',
    color_category_style('column', palette='sunset'),
    default_legend=False,
    default_widget=True,
    default_popup_hover=True,
    default_popup_click=True  # New feature
    title='Title'
)
```

</p>
</details>

## Popups

<details><summary>Hover Popup</summary>
<p>

Simple hover popup, now `popup_hover` is a Layer parameter that contains an array of `popup_element`

* From:

```python
from cartoframes.viz import Layer

Layer(
    'populated_places'
    popup={
        'hover': '$name'
    }
)
```

* To:

```python
from cartoframes.viz import Layer, popup_element

Layer(
    'populated_places',
    popup_hover=[
        popup_element('name')
    ]
)
```
</p>
</details>

<details><summary>Click Popup</summary>
<p>

Click popup with two values, now `popup_click` is also a Layer parameter that contains an array of `popup_element`

* From:

```python
from cartoframes.viz import Layer

Layer(
    'populated_places'
    popup={
        'click': ['$name', '$pop_max']
    }
)
```

* To:

```python
from cartoframes.viz import Layer, popup_element

Layer(
    'populated_places',
    popup_click=[
        popup_element('name'),
        popup_element('pop_max')
    ]
)
```
</p>
</details>

<details><summary>Multiple Popups</summary>
<p>

Multiple popups with custom titles

* From:

```python
from cartoframes.viz import Layer

Layer(
    'populated_places'
    popup={
        'click': [{
            'value': '$name',
            'title': 'Name'
        }, {
            'value': '$pop_max',
            'title': 'Pop Max'
        }],
        'hover': [{
            'value': '$name',
            'title': 'Name'
        }]
    }
)
```

* To:

```python
from cartoframes.viz import Layer, popup_element

Layer(
    'populated_places',
    popup_hover=[
        popup_element('name', title='Name'),
    ],
    popup_click=[
        popup_element('name', title='Name'),
        popup_element('pop_max', title='Pop Max')
    ]
)
```
</p>
</details>

## Widgets

<details><summary>Namespace</summary>
<p>

* From:

```python
from cartoframes.viz.widgets import formula_widget
```

* To:

```python
from cartoframes.viz import formula_widget
```

</p>
</details>

<details><summary>Widget class</summary>
<p>

* Don't create widgets through the `Widget` class anymore, extend the built-in widgets

</p>
</details>

## Legends

<details><summary>Namespace</summary>
<p>

* From:

```python
from cartoframes.viz import Legend
```

* To:

```python
from cartoframes.viz import color_bins_legend
```

</p>
</details>

<details><summary>Add legends to a class</summary>
<p>

* Don't create widgets through the `Legend` class anymore, extend the built-in legends
* `legend` parameter in Layer now is `legends` (plural)


* From:

```python
from cartoframes.viz import Map, Layer, Legend
Map(
  Layer(
    'table_name',
    style='...',
    legend=Legend('color-bins', title='Legend Title')
  )
)
```

* To:


```python
from cartoframes.viz import Map, Layer, color_bins_style, color_bins_legend, 
Map(
  Layer(
    'table_name',
    style=color_bins_style('column_name'),
    legends=color_bins_legend(title='Legend Title')
  )
)

# or

from cartoframes.viz import Map, Layer, color_bins_style, default_legend
Map(
  Layer(
    'table_name',
    style=color_bins_style('column_name'),
    legends=default_legend(title='Legend Title')
  )
)
```

Using multiple legends:

```python
from cartoframes.viz import Map, Layer, color_bins_style, basic_legend, default_legend
Map(
  Layer(
    'table_name',
    style=color_bins_style('column_name')
    legends=[
      basic_legend(title='Legend Title 1'),
      default_legend(title='Legend Title 2')
    ]
  )
)
```
</p>
</details>

<details><summary>Legend properties</summary>
<p>

Available properties for legends are changed to:

* "color" -> "color"
* "strokeColor" -> "stroke_color"
* "width" -> "size"
* "strokeWidth" -> "stroke_width"

* From:

```python
from cartoframes.viz import Map, Layer, Legend
Map(
  Layer(
    'table_name',
    style='...',
    legend=Legend('color-category', title='Legend Title', prop='strokeColor')
  )
)
```

* To:

```python
from cartoframes.viz import color_category_style, color_category_legend
Map(
  Layer(
    'table_name',
    style=color_category_style('column_name'),
    legends=color_category_legend('color-bins', title='Legend Title', prop='stroke_color')
  )
)
```
</p>
</details>