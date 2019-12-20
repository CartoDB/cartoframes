# RC1 Migration

Migration notes from `1.0b7` to `rc1`

* [Popups](#Popups)
* [Widgets](#Widgets)
* [Legends](#Legends)

## Popups

* [Related issue #1348](https://github.com/CartoDB/cartoframes/issues/1348)

<details><summary>Hover Popup</summary>
<p>

Simple hover popup, now `hover_popup` is a Layer parameter that contains an array of `popup_element`

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
    hover_popup=[
        popup_element('name')
    ]
)
```
</p>
</details>

<details><summary>Click Popup</summary>
<p>

Click popup with two values, now `click_popup` is also a Layer parameter that contains an array of `popup_element`

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
    click_popup=[
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
    click_popup=[
        popup_element('name', title='Name'),
        popup_element('pop_max', title='Pop Max')
    ],
    hover_popup=[
        popup_element('name', title='Name'),
    ]
)
```
</p>
</details>

## Widgets

* [Related issue #1349](https://github.com/CartoDB/cartoframes/issues/1349)

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

* [Related issue #1347](https://github.com/CartoDB/cartoframes/issues/1347)

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
from cartoframes.viz import Map, Layer, color_bins_legend
Map(
  Layer(
    'table_name',
    style='...',
    legends=color_bins_legend(title='Legend Title')
  )
)
```

```python
from cartoframes.viz import Map, Layer, color_bins_legend, color_continuous_legend
Map(
  Layer(
    'table_name',
    style='...'
    legends=[
      color_bins_legend(title='Legend Title 1'),
      color_continuous_legend(title='Legend Title 2')
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
* "strokeColor" -> "stroke-color"
* "width" -> "size"
* "strokeWidth" -> "stroke-width"

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
from cartoframes.viz import color_category_legend
Map(
  Layer(
    'table_name',
    style='...',
    legends=color_category_legend('color-bins', title='Legend Title', prop='stroke-color')
  )
)
```
</p>
</details>