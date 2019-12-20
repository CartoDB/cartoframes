# RC1 Migration

Migration notes from `1.0b7` to `rc1`

* [Widgets](#Widgets)
* [Legends](#Legends)

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
