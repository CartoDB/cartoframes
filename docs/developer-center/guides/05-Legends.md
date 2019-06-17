## Legends

There are different types of legends we can use in our visualization. These legends depend on the geometry of the layer and on the type of the data it is being represented.

### Legend Types

When we set the legend, we have to indicate the type of the legend. Current types are:

* Color
  * `color-category`
  * `color-bins`
  * `color-continuous`

* Size
  * `size-category`
  * `size-bins`
  * `size-continuous`

#### Classified by property

As we can see in the previous list of legend types, there're two types of legend regarding style: **color** and **size**. 

* **Color** types represent color style properties: `color` and `strokeColor`.
* **Size** types represent size style properties: `width` and `strokeWidth`.

#### Classified by data type

Each color and size legend legend types have three options: **category**, **bins**, and **continuous**.

* **Category** legends: for use with **categorical** data.
* **Bins** legends: for use with **numeric** data.
* **Continuous** legends: for use with **numeric** data.

By default, each of the previous types detects the geometry of the layer. However, we set explicitely the geometry, which is very useful when having several legens to identify the each one type.

### Default Legend

```py
Map(
    Layer('populated_places'),
    default_legend=True
)
```

### Add information

```py
Map(
    Layer(
        'populated_places',
        legend={
            'title': 'Populated Places',
            'description': 'This is a common dataset.',
            'footer': 'Source: CARTO'
        }
    )
)
```

![Add title, description and footer to the Legend](../../img/guides/legends/legends-1.png)

### Color Category

* color-category-point
* color-category-line
* color-category-polygon

Example:
```py
Map(
    Layer(
        'populated_places',
        'color: ramp(top($adm0name, 5), bold)',
        legend=Legend({
            'type': 'color-category-point'
        })
    )
)
```

![color-category legend](../../img/guides/legends/legends-2.png)

### Color Bins

* color-bins-point
* color-bins-line
* color-bins-polygon

Example:
```py
Map(
    Layer(
        'sfcta_congestion_roads',
        'color: ramp(globalEqIntervals($auto_speed, 5), purpor)',
        legend={
            'type': 'color-bins-line'
        }
    )
)
```

![color-bins legend](../../img/guides/legends/legends-3.png)

### Color Continuous

* color-continuous-point
* color-continuous-line
* color-continuous-polygon

Example:

```py
Map(
    Layer(
        'sf_neighborhoods',
        'color: ramp(linear($cartodb_id), sunset)',
        legend={
            'type': 'color-continuous-polygon',
            'prop': 'color'
        }
    )
)
```

![color-continuous legend](../../img/guides/legends/legends-4.png)

### Size Category

* size-category-point
* size-category-line

Example:
```py
Map(
    Layer(
        'populated_places',
        '''
        width: ramp(buckets($adm_0_cap_name, ["Capital", "City"]), [25, 5])
        strokeWidth: 1
        strokeColor: white
        ''',
        legend={
            'type': 'size-category-point'
        }
    )
)
```

![size-category legend](../../img/guides/legends/legends-5.png)

### Size Bins

* size-bins-point
* size-bins-line

Example:
```py
Map(
    Layer(
        'sfcta_congestion_roads',
        '''
        width: ramp(globalEqIntervals($auto_speed, 5), [1, 10])
        color: opacity(turquoise, 0.8)
        strokeWidth: 0.5
        strokeColor: opacity(blue,0.2)
        ''',
        legend={
            'type': 'size-bins-line'
        }
    )
)
```

![size-bins legend](../../img/guides/legends/legends-6.png)

### Size Continuous

* size-continuous-point
* size-continuous-line

Example:
```py
Map(
    Layer(
        'county_points_with_population',
        '''
        width: ramp(linear($estimate_total), [1, 80])
        color: opacity(turquoise, 0.8)
        strokeWidth: 0.5
        strokeColor: opacity(blue,0.4)
        order: asc(width())
        ''',
        legend={
            'type': 'size-continuous-point',
            'title':'Population by County'
        }
    )
)
```

![size-continuous legend](../../img/guides/legends/legends-7.png)

## Multiple Legends

Example:
```py
Map([
    Layer(
        'maximum_heat_index',
        'color: ramp(linear($value), purpor)',
        legend={
            'type': 'color-continuous-point',
            'title': 'Heat Index Values'
        }
    ),
    Layer(
        'county_points_with_population',
        '''
        width: ramp(globalEqIntervals($estimate_total,5), [2, 40])
        color: opacity(turquoise, 0.8)
        strokeWidth: 0.5
        strokeColor: opacity(blue,0.2)
        ''',
        legend={
            'type': 'size-continuous-point',
            'title': 'Population by Counti'
        }
    )
])
```

![Multiple legends](../../img/guides/legends/legends-8.png)